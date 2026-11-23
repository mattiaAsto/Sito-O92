"""Models for links, clubs, and sponsors."""

from app.extensions import db


class LinkGroup(db.Model):
    """Group of related links (e.g., 'Federazioni', 'Links utili')."""
    __tablename__ = 'link_group'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    links = db.relationship('Link', backref='group', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LinkGroup {self.title}>'


class Link(db.Model):
    """Individual link within a group."""
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('link_group.id'), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    href = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Link {self.label}>'


class Club(db.Model):
    """External club/association."""
    __tablename__ = 'club'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    href = db.Column(db.String(500), nullable=False)
    logo = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Club {self.label}>'


class Sponsor(db.Model):
    """Organization sponsor."""
    __tablename__ = 'sponsor'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    href = db.Column(db.String(500), nullable=False)
    logo = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Sponsor {self.label}>'
