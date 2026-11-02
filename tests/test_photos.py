import unittest
from datetime import datetime
from unittest.mock import patch

from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import Album, Photo, User

REMOTE = {
    "/2025/05 - Gara 1": ("2025 / 05 - Gara 1", "/2025/05 - Gara 1/a.jpg", datetime(2025, 5, 1)),
    "/2025/06 - Gara 2": ("2025 / 06 - Gara 2", "/2025/06 - Gara 2/c.jpg", datetime(2025, 6, 1)),
}
PHOTOS = {
    "/2025/05 - Gara 1": [
        ("/2025/05 - Gara 1/a.jpg", "a.jpg", datetime(2025, 5, 1)),
        ("/2025/05 - Gara 1/b.jpg", "b.jpg", datetime(2025, 5, 2)),
    ],
}

class PhotosTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "SQLALCHEMY_ENGINE_OPTIONS": {
                    "poolclass": StaticPool,
                    "connect_args": {"check_same_thread": False},
                },
                "WTF_CSRF_ENABLED": False,
                "DROPBOX_API_KEY": "token",
            }
        )
        with self.app.app_context():
            db.create_all()
            for email, flags in (("pm@example.com", {"is_photo_manager": True}), ("user@example.com", {})):
                user = User(first_name="A", last_name="B", email=email, **flags)
                user.set_password("password123")
                db.session.add(user)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, email):
        self.client.post("/auth/login", data={"email": email, "password": "password123"})

    def sync(self):
        with patch("app.photos.routes.fetch_albums", return_value=REMOTE):
            return self.client.post("/photos/sync")

    def test_sync_requires_photo_manager(self):
        self.assertEqual(self.client.post("/photos/sync").status_code, 302)
        self.login("user@example.com")
        self.assertEqual(self.client.post("/photos/sync").status_code, 403)

    def test_sync_gallery_and_lazy_album_page(self):
        self.login("pm@example.com")
        self.assertEqual(self.sync().status_code, 302)
        page = self.client.get("/gallery").get_data(as_text=True)
        self.assertIn("Gara 1", page)
        self.assertIn("Gara 2", page)
        self.assertIn("/photos/cover/", page)
        with self.app.app_context():
            album_id = db.session.execute(db.select(Album).filter_by(title="2025 / 05 - Gara 1")).scalar_one().id
            self.assertEqual(db.session.execute(db.select(db.func.count(Photo.id))).scalar_one(), 0)
        with patch("app.photos.routes.fetch_album_photos", return_value=PHOTOS["/2025/05 - Gara 1"]) as fetch:
            detail = self.client.get(f"/photos/album/{album_id}").get_data(as_text=True)
            self.client.get(f"/photos/album/{album_id}")
        self.assertEqual(fetch.call_count, 1)  # cached after the first visit
        self.assertEqual(detail.count("/photos/image/"), 4)  # small + large per photo
    def test_featured_albums_replace_recent(self):
        self.login("pm@example.com")
        self.sync()
        with self.app.app_context():
            album_id = db.session.execute(db.select(Album).filter_by(title="2025 / 05 - Gara 1")).scalar_one().id
        self.client.post(f"/photos/album/{album_id}/feature", data={"next": "/photos/"})
        page = self.client.get("/gallery").get_data(as_text=True)
        self.assertIn("Gara 1", page)
        self.assertNotIn("Gara 2", page)

    def test_resync_keeps_featured_and_removes_deleted(self):
        self.login("pm@example.com")
        self.sync()
        with self.app.app_context():
            album_id = db.session.execute(db.select(Album).filter_by(title="2025 / 05 - Gara 1")).scalar_one().id
        self.client.post(f"/photos/album/{album_id}/feature")
        with patch("app.photos.routes.fetch_albums", return_value={"/2025/05 - Gara 1": REMOTE["/2025/05 - Gara 1"]}):
            self.client.post("/photos/sync")
        with self.app.app_context():
            albums = db.session.execute(db.select(Album)).scalars().all()
            self.assertEqual([(a.title, a.is_featured) for a in albums], [("2025 / 05 - Gara 1", True)])

    def test_image_proxy(self):
        self.login("pm@example.com")
        self.sync()
        with self.app.app_context():
            album = db.session.execute(db.select(Album)).scalars().first()
            album.photos.append(Photo(dropbox_path="/x.jpg", name="x.jpg", taken_at=datetime(2025, 1, 1)))
            db.session.commit()
            album_id = album.id
        with patch("app.photos.routes.fetch_thumbnail", return_value=(b"jpg", "image/jpeg")):
            response = self.client.get("/photos/image/1/small")
            cover = self.client.get(f"/photos/cover/{album_id}/small")
        self.assertEqual(response.data, b"jpg")
        self.assertEqual(cover.data, b"jpg")
        self.assertEqual(self.client.get("/photos/image/1/huge").status_code, 404)
