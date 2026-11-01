import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import News, NewsImage, User


def png_bytes(size=(40, 30), mode="RGB"):
    buffer = io.BytesIO()
    Image.new(mode, size, "red").save(buffer, "PNG")
    return buffer.getvalue()


class NewsTestCase(unittest.TestCase):
    def setUp(self):
        self.upload_dir = tempfile.TemporaryDirectory()
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
                "UPLOAD_FOLDER": self.upload_dir.name,
            }
        )
        with self.app.app_context():
            db.create_all()
            for email, flags in (
                ("manager@example.com", {"is_news_manager": True}),
                ("admin@example.com", {"is_admin": True}),
                ("user@example.com", {}),
            ):
                user = User(first_name="A", last_name="B", email=email, **flags)
                user.set_password("password123")
                db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.upload_dir.cleanup()

    def client_for(self, email=None):
        client = self.app.test_client()
        if email:
            client.post("/auth/login", data={"email": email, "password": "password123"})
        return client

    def create_article(self, client, **overrides):
        data = {
            "title": "Titolo",
            "summary": "Sotto",
            "text": "Ciao\n\n![didascalia](Foto Uno.PNG)",
            "thumbnail": (io.BytesIO(png_bytes()), "thumb.png"),
            "photos": [(io.BytesIO(png_bytes()), "Foto Uno.PNG")],
        }
        data.update(overrides)
        return client.post("/news/create", data=data, content_type="multipart/form-data")

    def test_create_requires_news_manager(self):
        self.assertEqual(self.client_for().get("/news/create").status_code, 302)
        self.assertEqual(self.client_for("user@example.com").get("/news/create").status_code, 403)
        self.assertEqual(self.client_for("admin@example.com").get("/news/create").status_code, 403)
        self.assertEqual(self.client_for("manager@example.com").get("/news/create").status_code, 200)

    def test_article_must_be_verified_before_it_is_public(self):
        manager = self.client_for("manager@example.com")
        self.assertEqual(self.create_article(manager).status_code, 302)

        anonymous = self.client_for()
        self.assertNotIn("/news/1", anonymous.get("/").get_data(as_text=True))
        self.assertNotIn("/news/1", anonymous.get("/news/").get_data(as_text=True))
        self.assertEqual(anonymous.get("/news/1").status_code, 404)
        self.assertEqual(manager.get("/news/1").status_code, 200)
        self.assertEqual(manager.post("/news/1/verify").status_code, 403)

        admin = self.client_for("admin@example.com")
        self.assertEqual(admin.post("/news/1/verify").status_code, 302)
        self.assertIn("/news/1", anonymous.get("/").get_data(as_text=True))
        self.assertEqual(anonymous.get("/news/1").status_code, 200)

    def test_photos_are_stored_in_their_own_folder_and_rendered(self):
        self.create_article(self.client_for("manager@example.com"))
        with self.app.app_context():
            article = db.session.get(News, 1)
            image = article.images[0]
            self.assertEqual(image.original_name, "Foto Uno.PNG")
            self.assertTrue((Path(self.upload_dir.name) / "news" / "1" / image.filename).is_file())
            self.assertTrue(article.thumbnail_filename)
            self.assertNotEqual(article.thumbnail_filename, image.filename)
            photo_url = f"/media/news/1/{image.filename}"

        admin = self.client_for("admin@example.com")
        admin.post("/news/1/verify")
        anonymous = self.client_for()
        page = anonymous.get("/news/1").get_data(as_text=True)
        self.assertIn(f'src="{photo_url}"', page)
        self.assertIn("<figcaption>didascalia</figcaption>", page)
        self.assertEqual(anonymous.get(photo_url).status_code, 200)

    def test_media_of_unverified_news_is_private(self):
        self.create_article(self.client_for("manager@example.com"))
        with self.app.app_context():
            image = db.session.get(News, 1).images[0]
            url = f"/media/news/1/{image.filename}"
        self.assertEqual(self.client_for().get(url).status_code, 404)
        self.assertEqual(self.client_for("manager@example.com").get(url).status_code, 200)

    def test_media_rejects_path_traversal(self):
        client = self.client_for()
        self.assertEqual(client.get("/media/../app.db").status_code, 404)
        self.assertEqual(client.get("/media/news/1/../../x").status_code, 404)

    def test_same_filename_never_overwrites(self):
        manager = self.client_for("manager@example.com")
        photo = lambda: (io.BytesIO(png_bytes()), "same.png")
        self.create_article(manager, photos=[photo(), photo()], thumbnail=photo())
        with self.app.app_context():
            names = [i.filename for i in db.session.get(News, 1).images]
            files = list((Path(self.upload_dir.name) / "news" / "1").iterdir())
        self.assertEqual(len(set(names)), 2)
        self.assertEqual(len(files), 3)

    def test_non_image_is_rejected_even_with_image_extension(self):
        response = self.create_article(
            self.client_for("manager@example.com"),
            photos=[(io.BytesIO(b"<script>alert(1)</script>"), "evil.png")],
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("non è un&#39;immagine valida", response.get_data(as_text=True))
        with self.app.app_context():
            self.assertEqual(News.query.count(), 0)
            self.assertFalse((Path(self.upload_dir.name) / "news").exists())

    def test_images_are_reencoded_and_downscaled(self):
        self.create_article(
            self.client_for("manager@example.com"),
            photos=[(io.BytesIO(png_bytes((3000, 2000))), "big.png")],
        )
        with self.app.app_context():
            image = db.session.get(News, 1).images[0]
            path = Path(self.upload_dir.name) / "news" / "1" / image.filename
            with Image.open(path) as stored:
                self.assertLessEqual(max(stored.size), 1600)

    def test_missing_photo_reference_warns(self):
        response = self.client_for("manager@example.com").post(
            "/news/create",
            data={"title": "T", "text": "![x](non-caricata.jpg)"},
            follow_redirects=True,
        )
        self.assertIn("non-caricata.jpg", response.get_data(as_text=True))

    def test_only_admin_can_delete_and_files_are_removed(self):
        manager = self.client_for("manager@example.com")
        self.create_article(manager)
        folder = Path(self.upload_dir.name) / "news" / "1"
        self.assertTrue(folder.is_dir())
        self.assertEqual(manager.post("/news/1/delete").status_code, 403)

        self.assertEqual(self.client_for("admin@example.com").post("/news/1/delete").status_code, 302)
        self.assertFalse(folder.exists())
        with self.app.app_context():
            self.assertEqual(News.query.count(), 0)
            self.assertEqual(NewsImage.query.count(), 0)

    def test_pending_list_is_admin_only(self):
        self.assertEqual(self.client_for("manager@example.com").get("/news/pending").status_code, 403)
        self.assertEqual(self.client_for("admin@example.com").get("/news/pending").status_code, 200)


if __name__ == "__main__":
    unittest.main()
