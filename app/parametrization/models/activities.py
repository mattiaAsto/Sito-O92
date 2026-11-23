"""Models for activities and race disciplines."""

from app.extensions import db


class Activity(db.Model):
    """Activity/event for the Attività page."""
    __tablename__ = 'activity'

    id = db.Column(db.Integer, primary_key=True)
    tab = db.Column(db.String(50), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    caption = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Activity {self.tab}>'


class Discipline(db.Model):
    """Race discipline for the Gare page."""
    __tablename__ = 'discipline'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Discipline {self.name}>'
