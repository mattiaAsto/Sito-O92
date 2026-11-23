"""Models for documents and their page mappings."""

from app.extensions import db


class Document(db.Model):
    """PDF or document file."""
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    label = db.Column(db.String(255), nullable=False)
    folder = db.Column(db.String(50), nullable=False)  # e.g., 'contacts', 'whats_orienteering'
    file = db.Column(db.String(255), nullable=False)
    blueprint = db.Column(db.String(50), nullable=False)  # e.g., 'main', 'shop', 'calendar'
    static_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Document {self.key}>'


class DocumentMapping(db.Model):
    """Maps documents to pages for display."""
    __tablename__ = 'document_mapping'

    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(100), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    document = db.relationship('Document', backref='mappings')

    __table_args__ = (
        db.UniqueConstraint('page_name', 'document_id', name='_page_document_uc'),
    )

    def __repr__(self):
        return f'<DocumentMapping {self.page_name}>'
