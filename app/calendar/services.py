from datetime import datetime
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models import CalendarActivity


def get_upcoming_activities(activity_type, limit=5, now=None):
    # Datetimes are stored as Zurich wall-clock time, so compare against naive local time.
    now = now or datetime.now(ZoneInfo("Europe/Zurich")).replace(tzinfo=None)
    return db.session.execute(
        db.select(CalendarActivity)
        .where(
            CalendarActivity.activity_type == activity_type,
            CalendarActivity.ends_at > now,
        )
        .order_by(CalendarActivity.starts_at, CalendarActivity.id)
        .limit(limit)
    ).scalars().all()


def get_upcoming_inscription_deadlines(limit=3, today=None):
    today = today or datetime.now(ZoneInfo("Europe/Zurich")).date()
    return db.session.execute(
        db.select(CalendarActivity)
        .where(CalendarActivity.inscription_delay_date >= today)
        .order_by(CalendarActivity.inscription_delay_date, CalendarActivity.starts_at, CalendarActivity.id)
        .limit(limit)
    ).scalars().all()


def get_next_activity(activity_type, now=None):
    activities = get_upcoming_activities(activity_type, limit=1, now=now)
    return activities[0] if activities else None


def get_calendar_activities(start_at=None, end_at=None):
    query = db.select(CalendarActivity)
    if start_at is not None:
        query = query.where(CalendarActivity.ends_at > start_at)
    if end_at is not None:
        query = query.where(CalendarActivity.starts_at < end_at)
    return db.session.execute(
        query.order_by(CalendarActivity.starts_at, CalendarActivity.id)
    ).scalars().all()
