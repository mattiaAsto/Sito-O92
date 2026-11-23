"""Models for people management (committee, monitors, contacts)."""

from app.extensions import db


class CommitteeMember(db.Model):
    """Committee member of the organization."""
    __tablename__ = 'committee_member'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<CommitteeMember {self.name}>'


class OtherRole(db.Model):
    """Person with other organizational role."""
    __tablename__ = 'other_role'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<OtherRole {self.name}>'


class Monitor(db.Model):
    """Training monitor/instructor."""
    __tablename__ = 'monitor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Monitor {self.name}>'


class Contact(db.Model):
    """Contact person for specific role/function."""
    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Contact {self.role} - {self.name}>'
