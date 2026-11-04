from datetime import datetime
import hashlib
from zoneinfo import ZoneInfo

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, Numeric
from sqlalchemy.dialects import mysql
from sqlalchemy.types import LargeBinary
from werkzeug.security import check_password_hash, generate_password_hash

from app.calendar.palette import ACTIVITY_CATEGORIES
from app.extensions import db


class CalendarActivity(db.Model):
    __tablename__ = "calendar_activities"
    __table_args__ = (
        CheckConstraint(
            "activity_type IN ('allenamento', 'gara', 'attivita')",
            name="ck_calendar_activities_type",
        ),
        CheckConstraint(
            "category IN "
            "('training_wednesday', 'training_friday', 'race_ticino', "
            "'race_switzerland', 'other_activity', 'camp')",
            name="ck_calendar_activities_category",
        ),
        CheckConstraint(
            "ends_at >= starts_at",
            name="ck_calendar_activities_end_after_start",
        ),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL "
            "AND latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)",
            name="ck_calendar_activities_coordinates",
        ),
        CheckConstraint(
            "(category IN ('training_wednesday', 'training_friday') "
            "AND activity_type = 'allenamento') OR "
            "(category IN ('race_ticino', 'race_switzerland') "
            "AND activity_type = 'gara') OR "
            "(category IN ('other_activity', 'camp') "
            "AND activity_type = 'attivita')",
            name="ck_calendar_activities_category_type",
        ),
        CheckConstraint(
            "inscription_delay_date IS NULL OR activity_type <> 'allenamento'",
            name="ck_calendar_activities_delay_not_training",
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity_type = db.Column(db.String(20), nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=False)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    inscription_delay_date = db.Column(db.Date, index=True)

    @property
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def schedule_label(self):
        """Full schedule for the detail page: trainings show hours, races only dates."""
        starts, ends = self.starts_at, self.ends_at
        same_day = starts.date() == ends.date()
        day = starts.strftime("%d.%m.%Y")
        if self.activity_type == "allenamento" and same_day:
            return f"{day}, {starts:%H:%M} – {ends:%H:%M}"
        if self.activity_type == "gara":
            return day if same_day else f"{day} – {ends:%d.%m.%Y}"
        if same_day:
            return f"{day}, {starts:%H:%M} – {ends:%H:%M}"
        return f"{starts:%d.%m.%Y %H:%M} – {ends:%d.%m.%Y %H:%M}"

    @property
    def date_label(self):
        """Date only (or date range for multi-day activities)."""
        starts, ends = self.starts_at, self.ends_at
        if starts.date() == ends.date():
            return starts.strftime("%d.%m.%Y")
        return f"{starts:%d.%m.} – {ends:%d.%m.%Y}"

    @property
    def hours_label(self):
        """Hours only, without the date (None for races)."""
        if self.activity_type == "gara":
            return None
        return f"{self.starts_at:%H:%M} – {self.ends_at:%H:%M}"

    @property
    def time_label(self):
        """Short time shown inside calendar cells (None for races)."""
        if self.activity_type == "gara":
            return None
        if self.activity_type == "allenamento":
            return f"{self.starts_at:%H:%M} – {self.ends_at:%H:%M}"
        return f"{self.starts_at:%H:%M}"

    @property
    def category_label(self):
        return ACTIVITY_CATEGORIES[self.category]["label"]

    @property
    def color(self):
        return ACTIVITY_CATEGORIES[self.category]["color"]


class VanBooking(db.Model):
    """A period (inclusive dates) in which a van is not available for rental."""

    __tablename__ = "van_bookings"
    __table_args__ = (
        CheckConstraint("van IN ('trafic', 'vivaro')", name="ck_van_bookings_van"),
        CheckConstraint("end_date >= start_date", name="ck_van_bookings_end_after_start"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    van = db.Column(db.String(20), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    note = db.Column(db.String(200))
    created_by_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="SET NULL"))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("Europe/Zurich")).replace(tzinfo=None),
    )


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
    is_calendar_manager = db.Column(db.Boolean, nullable=False, default=False, server_default='0')

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

    @property
    def storage_prefix(self):
        return f"news/{self.id}"

    @property
    def thumbnail_key(self):
        if not self.thumbnail_filename:
            return None
        return f"{self.storage_prefix}/{self.thumbnail_filename}"


class Album(db.Model):
    """A first-level sub-folder of the Dropbox photo folder, mirrored by the photo sync."""

    __tablename__ = "photo_albums"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dropbox_path = db.Column(db.String(500), nullable=False, unique=True)  # relative to the shared folder
    title = db.Column(db.String(255), nullable=False)
    cover_path = db.Column(db.String(600), nullable=False)  # first photo, relative to the shared folder
    is_featured = db.Column(db.Boolean, nullable=False, default=False, server_default="0", index=True)
    date = db.Column(db.DateTime, nullable=False, index=True)  # from the folder name, else newest photo
    photos_loaded_at = db.Column(db.DateTime)  # when the full photo list was last read from Dropbox

    photos = db.relationship(
        "Photo", back_populates="album", cascade="all, delete-orphan", order_by="Photo.taken_at, Photo.id"
    )

    @property
    def cache_token(self):
        return hashlib.sha1(self.cover_path.encode("utf-8")).hexdigest()[:10]


class Photo(db.Model):
    """A photo inside an album; the image itself stays on Dropbox and is proxied by the site."""

    __tablename__ = "photo_photos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_id = db.Column(
        db.Integer, db.ForeignKey("photo_albums.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dropbox_path = db.Column(db.String(600), nullable=False)  # relative to the shared folder
    name = db.Column(db.String(255), nullable=False)
    taken_at = db.Column(db.DateTime, nullable=False)

    album = db.relationship("Album", back_populates="photos")

    @property
    def cache_token(self):
        # Changes with the Dropbox path, so reused ids never show another photo's cached image.
        return hashlib.sha1(self.dropbox_path.encode("utf-8")).hexdigest()[:10]


class BlogPost(db.Model):
    """A long-form story written by a user; needs admin verification to be public."""

    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(
        db.Integer, db.ForeignKey("Users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(300))
    text = db.Column(db.Text().with_variant(mysql.MEDIUMTEXT(), "mysql"), nullable=False)  # markdown
    cover_filename = db.Column(db.String(255))  # stored name inside the post's folder
    is_verified = db.Column(db.Boolean, nullable=False, default=False, server_default="0", index=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
        default=lambda: datetime.now(ZoneInfo("Europe/Zurich")),
    )

    author = db.relationship("User")
    images = db.relationship(
        "BlogImage", back_populates="post", cascade="all, delete-orphan", order_by="BlogImage.id"
    )

    @property
    def storage_prefix(self):
        return f"blog/{self.id}"

    @property
    def cover_key(self):
        if not self.cover_filename:
            return None
        return f"{self.storage_prefix}/{self.cover_filename}"


class BlogImage(db.Model):
    """A photo uploaded for use inside a blog post's text."""

    __tablename__ = "blog_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = db.Column(db.String(255), nullable=False)  # random stored name
    original_name = db.Column(db.String(255), nullable=False)  # name used in the markdown

    post = db.relationship("BlogPost", back_populates="images")
