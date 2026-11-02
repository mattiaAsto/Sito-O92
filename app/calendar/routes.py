from datetime import date, datetime, time

from flask import abort, jsonify, redirect, render_template, request, url_for

from app.calendar import calendar
from app.calendar.palette import ACTIVITY_CATEGORIES
from app.calendar.services import get_calendar_activities, get_upcoming_inscription_deadlines
from app.extensions import db
from app.models import CalendarActivity


@calendar.route("/calendar")
def calendario():
    return render_template(
        "calendar/index.html",
        activity_categories=ACTIVITY_CATEGORIES,
        deadlines=get_upcoming_inscription_deadlines(),
    )


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
    return render_template("calendar/activity.html", activity=activity)
