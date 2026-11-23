"""Models for shop materials."""

from app.extensions import db


class ShopMaterial(db.Model):
    """Official O-92 material/merchandise for sale."""
    __tablename__ = 'shop_material'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text, nullable=True)
    contact_name = db.Column(db.String(100), nullable=True)
    contact_email = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    prices = db.relationship('ShopMaterialPrice', backref='material', lazy=True, cascade='all, delete-orphan')
    sizes = db.relationship('ShopMaterialSize', backref='material', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ShopMaterial {self.name}>'


class ShopMaterialPrice(db.Model):
    """Price variant for a shop material."""
    __tablename__ = 'shop_material_price'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('shop_material.id'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)  # e.g., "100.-", "85.50"
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<ShopMaterialPrice {self.material_id}:{self.label}>'


class ShopMaterialSize(db.Model):
    """Size variant for a shop material."""
    __tablename__ = 'shop_material_size'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('shop_material.id'), nullable=False)
    group = db.Column(db.String(50), nullable=False)  # e.g., 'Donna', 'Uomo', 'Bambino'
    sizes = db.Column(db.String(255), nullable=False)  # e.g., 'S / M / L', '150 / 160'
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<ShopMaterialSize {self.material_id}:{self.group}>'
