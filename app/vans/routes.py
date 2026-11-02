from datetime import date
from functools import wraps

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.email import send_email
from app.extensions import db
from app.models import VanBooking
from app.vans import vans
from app.vans.forms import VANS, VAN_COLORS, BookingForm, RentalRequestForm
from app.vans.services import MONTH_NAMES, month_grid, parse_month, shift_month

VANS_EMAIL = "furgoni@o-92.ch"


def van_manager_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not (current_user.is_van_manager or current_user.is_admin):
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def _can_manage():
    return current_user.is_authenticated and (
        current_user.is_van_manager or current_user.is_admin
    )


def _render_page(request_form, booking_form, month_arg):
    first_day = parse_month(month_arg)
    return render_template(
        "vans/index.html",
        request_form=request_form,
        booking_form=booking_form,
        weeks=month_grid(first_day),
        month_label=f"{MONTH_NAMES[first_day.month - 1]} {first_day.year}",
        prev_month=shift_month(first_day, -1).strftime("%Y-%m"),
        next_month=shift_month(first_day, 1).strftime("%Y-%m"),
        vans=VANS,
        van_colors=VAN_COLORS,
        today=date.today(),
        can_manage=_can_manage(),
        vans_email=VANS_EMAIL,
    )


@vans.route("/furgoni", methods=["GET", "POST"])
def index():
    request_form = RentalRequestForm(prefix="rent")
    if request_form.validate_on_submit():
        data = request_form
        body = (
            "Nuova richiesta di noleggio furgone dal sito.\n\n"
            f"Email: {data.email.data}\n"
            f"Telefono: {data.phone_prefix.data} {data.phone_number.data}\n"
            f"Dal: {data.start_date.data:%d.%m.%Y}\n"
            f"Al: {data.end_date.data:%d.%m.%Y}\n\n"
            f"Messaggio:\n{data.message.data or '-'}"
        )
        try:
            send_email(
                subject=(
                    "Richiesta noleggio furgone "
                    f"{data.start_date.data:%d.%m.%Y} – {data.end_date.data:%d.%m.%Y}"
                ),
                recipients=[VANS_EMAIL],
                body=body,
                reply_to=data.email.data,
            )
        except Exception:
            current_app.logger.exception("Van rental request email failed")
            flash("Non è stato possibile inviare la richiesta. Riprova più tardi.", "error")
        else:
            flash("Grazie! La tua richiesta è stata inviata.", "success")
            return redirect(url_for("vans.index", _anchor="richiesta"))
    return _render_page(request_form, BookingForm(prefix="book"), request.args.get("month"))


@vans.route("/furgoni/occupazione", methods=["POST"])
@van_manager_required
def add_booking():
    form = BookingForm(prefix="book")
    if form.validate_on_submit():
        db.session.add(
            VanBooking(
                van=form.van.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                note=form.note.data or None,
                created_by_id=current_user.id,
            )
        )
        db.session.commit()
        flash("Occupazione aggiunta.", "success")
        return redirect(
            url_for("vans.index", month=form.start_date.data.strftime("%Y-%m"), _anchor="calendario")
        )
    start = form.start_date.data
    page = _render_page(
        RentalRequestForm(prefix="rent"), form, start.strftime("%Y-%m") if start else None
    )
    return page, 400


@vans.route("/furgoni/occupazione/<int:booking_id>/elimina", methods=["POST"])
@van_manager_required
def delete_booking(booking_id):
    booking = db.get_or_404(VanBooking, booking_id)
    month = booking.start_date.strftime("%Y-%m")
    db.session.delete(booking)
    db.session.commit()
    flash("Occupazione rimossa.", "success")
    return redirect(url_for("vans.index", month=month, _anchor="calendario"))
