import calendar as pycalendar
from datetime import date, timedelta

from app.extensions import db
from app.models import VanBooking

MONTH_NAMES = (
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
)


def parse_month(value):
    """Return the first day of the month in 'YYYY-MM' (current month if missing/invalid)."""
    try:
        year, month = (int(part) for part in value.split("-"))
        return date(year, month, 1)
    except (AttributeError, TypeError, ValueError):
        return date.today().replace(day=1)


def shift_month(first_day, offset):
    index = first_day.year * 12 + first_day.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


def month_grid(first_day):
    """Weeks (Monday first) of days; each day is {'date', 'in_month', 'bookings'}."""
    weeks = pycalendar.Calendar(firstweekday=0).monthdatescalendar(first_day.year, first_day.month)
    grid_start, grid_end = weeks[0][0], weeks[-1][-1]
    bookings = db.session.execute(
        db.select(VanBooking)
        .where(VanBooking.start_date <= grid_end, VanBooking.end_date >= grid_start)
        .order_by(VanBooking.start_date, VanBooking.van, VanBooking.id)
    ).scalars().all()

    by_day = {}
    for booking in bookings:
        day = max(booking.start_date, grid_start)
        last = min(booking.end_date, grid_end)
        while day <= last:
            by_day.setdefault(day, []).append(booking)
            day += timedelta(days=1)

    return [
        [
            {
                "date": day,
                "in_month": day.month == first_day.month,
                "bookings": by_day.get(day, []),
            }
            for day in week
        ]
        for week in weeks
    ]
