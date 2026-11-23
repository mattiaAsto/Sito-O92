"""Models for calendar categories."""

from app.extensions import db


class CalendarCategory(db.Model):
    """Calendar event category with color coding."""
    __tablename__ = 'calendar_category'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    activity_type = db.Column(db.String(20), nullable=False)  # allenamento, gara, attivita
    label = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False)  # hex color
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<CalendarCategory {self.key}>'
