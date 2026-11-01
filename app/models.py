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
    __tablename__ = "shop_products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_shop_products_price_nonnegative"),
        CheckConstraint(
            "listing_type IN ('team', 'used')",
            name="ck_shop_products_listing_type",
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(40), nullable=False)
    listing_type = db.Column(
        db.String(20), nullable=False, default="team", server_default="team"
    )
    price = db.Column(Numeric(10, 2), nullable=False)
    image_filename = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, nullable=False, default=True, server_default="1")


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)  # markdown
    summary = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, nullable=False, default=False, server_default="0", index=True)
    thumbnail_filename = db.Column(db.String(255))  # file inside app/news/static/<id>/
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
        default=lambda: datetime.now(ZoneInfo("Europe/Zurich")),
    )
