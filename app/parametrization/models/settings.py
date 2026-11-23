"""Models for site-wide settings."""

from app.extensions import db


class Setting(db.Model):
    """Site-wide configuration setting."""
    __tablename__ = 'setting'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(20), default='text')  # text, email, url, integer, boolean
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Setting {self.key}>'
