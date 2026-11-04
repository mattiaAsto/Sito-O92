from datetime import date, datetime, time, timedelta
from functools import wraps

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.calendar import calendar
from app.calendar.coordinates import format_coordinates, parse_coordinates
from app.calendar.forms import ActivityForm
from app.calendar.palette import ACTIVITY_CATEGORIES
from app.calendar.services import get_calendar_activities, get_upcoming_inscription_deadlines
from app.extensions import db
from app.models import CalendarActivity


def calendar_manager_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not _can_manage():
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def _can_manage():
    return current_user.is_authenticated and (
        current_user.is_calendar_manager or current_user.is_admin
    )


def _apply_form(activity, form):
    category = form.category.data
    activity.category = category
    activity.activity_type = ACTIVITY_CATEGORIES[category]["activity_type"]
    activity.title = form.title.data
    activity.description = form.description.data or None
    activity.starts_at = form.starts_at.data
    activity.ends_at = form.ends_at.data
    activity.location = form.location.data or None
    if form.coordinates.data:
        activity.latitude, activity.longitude = parse_coordinates(form.coordinates.data)
    else:
        activity.latitude = activity.longitude = None
    activity.inscription_delay_date = (
        None if activity.activity_type == "allenamento" else form.inscription_delay_date.data
    )


@calendar.route("/calendar")
def calendario():
    return render_template(
        "calendar/index.html",
        activity_categories=ACTIVITY_CATEGORIES,
        deadlines=get_upcoming_inscription_deadlines(),
        can_manage=_can_manage(),
    )


def _render_form(form, activity):
    return render_template(
        "calendar/activity_form.html",
        form=form,
        activity=activity,
        training_categories=[
            key for key, data in ACTIVITY_CATEGORIES.items()
            if data["activity_type"] == "allenamento"
        ],
    ), (400 if form.is_submitted() else 200)


@calendar.route("/calendar/activity/new", methods=["GET", "POST"])
@calendar_manager_required
def create_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        repeats = (form.weekly_repeats.data or 1) if form.is_training else 1
        first = None
        for week in range(repeats):
            activity = CalendarActivity()
            _apply_form(activity, form)
            offset = timedelta(weeks=week)
            activity.starts_at += offset
            activity.ends_at += offset
            db.session.add(activity)
            first = first or activity
        db.session.commit()
        flash("Attività create." if repeats > 1 else "Attività creata.", "success")
        return redirect(url_for("calendar.activity_detail", activity_id=first.id))
    return _render_form(form, None)


@calendar.route("/calendar/activity/<int:activity_id>/edit", methods=["GET", "POST"])
@calendar_manager_required
def edit_activity(activity_id):
    activity = db.get_or_404(CalendarActivity, activity_id)
    form = ActivityForm(obj=activity, allow_repeat=False)
    if request.method == "GET":
        form.coordinates.data = format_coordinates(activity.latitude, activity.longitude)
    if form.validate_on_submit():
        _apply_form(activity, form)
        db.session.commit()
        flash("Attività aggiornata.", "success")
        return redirect(url_for("calendar.activity_detail", activity_id=activity.id))
    return _render_form(form, activity)


@calendar.route("/calendar/activity/<int:activity_id>/delete", methods=["POST"])
@calendar_manager_required
def delete_activity(activity_id):
    activity = db.get_or_404(CalendarActivity, activity_id)
    db.session.delete(activity)
    db.session.commit()
    flash("Attività eliminata.", "success")
    return redirect(url_for("calendar.calendario"))


@calendar.route("/calendar/events")
def events():
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        abort(400, description="Both start and end dates are required.")

    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        abort(400, description="Dates must use the YYYY-MM-DD format.")

    if start_date.isoformat() != start or end_date.isoformat() != end:
        abort(400, description="Dates must use the YYYY-MM-DD format.")
    if end_date <= start_date:
        abort(400, description="The end date must be after the start date.")

    start_at = datetime.combine(start_date, time.min)
    end_at = datetime.combine(end_date, time.min)
    activities = get_calendar_activities(start_at, end_at)
    return jsonify(
        events=[
            {
                "id": activity.id,
                "title": activity.title,
                "start": activity.starts_at.isoformat(),
                "end": activity.ends_at.isoformat(),
                "time": activity.time_label,
                "location": activity.location,
                "activity_type": activity.activity_type,
                "category": activity.category,
                "category_label": activity.category_label,
                "color": activity.color,
            }
            for activity in activities
        ]
    )


@calendar.route("/calendar/activity/<int:activity_id>")
def activity_detail(activity_id):
    activity = db.session.get(CalendarActivity, activity_id)
    if activity is None:
        abort(404)
    return render_template(
        "calendar/activity.html", activity=activity, can_manage=_can_manage()
    )
