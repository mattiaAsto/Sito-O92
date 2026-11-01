from datetime import datetime
from zoneinfo import ZoneInfo

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, Numeric
from sqlalchemy.types import LargeBinary
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(LargeBinary, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False, server_default='0')
    is_photo_manager = db.Column(db.Boolean, nullable=False, default=False, server_default='0')
    is_van_manager = db.Column(db.Boolean, nullable=False, default=False, server_default='0')
    is_news_manager = db.Column(db.Boolean, nullable=False, default=False, server_default='0')

    def set_password(self, password):
        self.password = generate_password_hash(password).encode("utf-8")

    def check_password(self, password):
        return check_password_hash(self.password.decode("utf-8"), password)


class Product(db.Model):
    """A shop item: official team clothing (admins) or a member's used-item listing."""

    __tablename__ = "shop_products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_shop_products_price_nonnegative"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(
        db.Integer, db.ForeignKey("Users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(40), nullable=False)
    size = db.Column(db.String(20))
    price = db.Column(Numeric(10, 2), nullable=False)
    contact_phone = db.Column(db.String(30))
    is_official_clothing = db.Column(
        db.Boolean, nullable=False, default=False, server_default="0", index=True
    )
    is_verified = db.Column(db.Boolean, nullable=False, default=False, server_default="0", index=True)
    is_available = db.Column(db.Boolean, nullable=False, default=True, server_default="1")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
        default=lambda: datetime.now(ZoneInfo("Europe/Zurich")),
    )

    seller = db.relationship("User")
    images = db.relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.id",
    )

    @property
    def storage_prefix(self):
        return f"shop/{self.id}"

    @property
    def image_keys(self):
        return [f"{self.storage_prefix}/{image.filename}" for image in self.images]

    @property
    def cover_key(self):
        keys = self.image_keys
        return keys[0] if keys else None


class ProductImage(db.Model):
    __tablename__ = "shop_product_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("shop_products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = db.Column(db.String(255), nullable=False)  # random stored name

    product = db.relationship("Product", back_populates="images")


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)  # markdown
    summary = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, nullable=False, default=False, server_default="0", index=True)
    thumbnail_filename = db.Column(db.String(255))  # stored name inside the article's folder
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
        default=lambda: datetime.now(ZoneInfo("Europe/Zurich")),
    )

    images = db.relationship(
        "NewsImage", back_populates="news", cascade="all, delete-orphan", order_by="NewsImage.id"
    )

    @property
    def storage_prefix(self):
        return f"news/{self.id}"

    @property
    def thumbnail_key(self):
        if not self.thumbnail_filename:
            return None
        return f"{self.storage_prefix}/{self.thumbnail_filename}"


class NewsImage(db.Model):
    """A photo uploaded for use inside an article's text."""

    __tablename__ = "news_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    news_id = db.Column(
        db.Integer, db.ForeignKey("news.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = db.Column(db.String(255), nullable=False)  # random stored name
    original_name = db.Column(db.String(255), nullable=False)  # name used in the markdown
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("Europe/Zurich")),
    )

    news = db.relationship("News", back_populates="images")
