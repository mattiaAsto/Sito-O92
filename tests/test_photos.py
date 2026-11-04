import unittest
from datetime import datetime
from unittest.mock import patch

from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import Album, Photo, User

REMOTE = {
    "/2025/05 - Gara 1": ("2025 / 05 - Gara 1", datetime(2025, 5, 1)),
    "/2025/06 - Gara 2": ("2025 / 06 - Gara 2", datetime(2025, 6, 1)),
}
GARA1 = "/2025/05 - Gara 1"
GARA1_PHOTOS = [
    (GARA1 + "/a.jpg", "a.jpg", datetime(2025, 5, 1)),
    (GARA1 + "/b.jpg", "b.jpg", datetime(2025, 5, 2)),
]

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

    def album_id(self, title="2025 / 05 - Gara 1"):
        with self.app.app_context():
            return db.session.execute(db.select(Album).filter_by(title=title)).scalar_one().id

    def show(self, album_id):
        with patch("app.photos.routes.fetch_album_photos", return_value=GARA1_PHOTOS) as fetch, patch(
            "app.photos.routes.fetch_thumbnail", return_value=(b"jpg", "image/jpeg")
        ) as thumb:
            self.client.post(f"/photos/album/{album_id}/visibility")
        self.thumb = thumb
        return fetch

    def test_sync_only_stores_names_and_gallery_starts_empty(self):
        self.login("pm@example.com")
        self.assertEqual(self.sync().status_code, 302)
        with self.app.app_context():
            self.assertEqual(db.session.execute(db.select(db.func.count(Album.id))).scalar_one(), 2)
            self.assertEqual(db.session.execute(db.select(db.func.count(Photo.id))).scalar_one(), 0)
        page = self.client.get("/gallery").get_data(as_text=True)
        self.assertNotIn("Gara 1", page)
        self.assertIn("Gara 1", self.client.get("/photos/manage").get_data(as_text=True))

    def test_making_visible_loads_photos_and_shows_album(self):
        self.login("pm@example.com")
        self.sync()
        album_id = self.album_id()
        fetch = self.show(album_id)
        self.assertEqual(fetch.call_count, 1)
        self.thumb.assert_called_once_with(GARA1 + "/a.jpg", "small")  # cover created on publish
        page = self.client.get("/gallery").get_data(as_text=True)
        self.assertIn("Gara 1", page)
        self.assertNotIn("Gara 2", page)
        self.assertIn("/photos/cover/", page)
        with patch("app.photos.routes.fetch_album_photos") as again:
            detail = self.client.get(f"/photos/album/{album_id}").get_data(as_text=True)
        self.assertEqual(again.call_count, 0)  # still fresh
        self.assertEqual(detail.count("/photos/image/"), 4)  # small + large per photo

    def test_hidden_album_is_not_public(self):
        self.login("pm@example.com")
        self.sync()
        album_id = self.album_id()
        anon = self.app.test_client()
        self.assertEqual(anon.get(f"/photos/album/{album_id}").status_code, 404)
        self.assertEqual(anon.get(f"/photos/cover/{album_id}/small").status_code, 404)

    def test_failed_load_keeps_album_hidden(self):
        self.login("pm@example.com")
        self.sync()
        album_id = self.album_id()
        with patch("app.photos.routes.fetch_album_photos", side_effect=RuntimeError("boom")):
            self.client.post(f"/photos/album/{album_id}/visibility")
        with self.app.app_context():
            self.assertFalse(db.session.get(Album, album_id).is_visible)

    def test_resync_keeps_visibility_and_removes_deleted(self):
        self.login("pm@example.com")
        self.sync()
        self.show(self.album_id())
        with patch("app.photos.routes.fetch_albums", return_value={GARA1: REMOTE[GARA1]}):
            self.client.post("/photos/sync")
        with self.app.app_context():
            albums = db.session.execute(db.select(Album)).scalars().all()
            self.assertEqual([(a.title, a.is_visible) for a in albums], [("2025 / 05 - Gara 1", True)])

    def test_image_proxy(self):
        self.login("pm@example.com")
        self.sync()
        album_id = self.album_id()
        self.show(album_id)
        with patch("app.photos.routes.fetch_thumbnail", return_value=(b"jpg", "image/jpeg")):
            response = self.client.get("/photos/image/1/small")
            cover = self.client.get(f"/photos/cover/{album_id}/small")
        self.assertEqual(response.data, b"jpg")
        self.assertEqual(cover.data, b"jpg")
        self.assertEqual(self.client.get("/photos/image/1/huge").status_code, 404)