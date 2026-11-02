import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import BlogImage, BlogPost, User
from tests.test_news import png_bytes


class BlogTestCase(unittest.TestCase):
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
                ("admin@example.com", {"is_admin": True}),
                ("author@example.com", {}),
                ("other@example.com", {}),
            ):
                user = User(first_name="Gianni", last_name="Verdi", email=email, **flags)
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

    def create_post(self, client, **overrides):
        data = {
            "title": "Gara in Giappone",
            "summary": "Una trasferta",
            "text": "Ciao\n\n![didascalia](Foto Uno.PNG)",
            "cover": (io.BytesIO(png_bytes()), "cover.png"),
            "photos": [(io.BytesIO(png_bytes()), "Foto Uno.PNG")],
        }
        data.update(overrides)
        return client.post("/blog/create", data=data, content_type="multipart/form-data")

    def test_create_requires_login(self):
        self.assertEqual(self.client_for().get("/blog/create").status_code, 302)
        self.assertEqual(self.client_for("author@example.com").get("/blog/create").status_code, 200)

    def test_post_must_be_verified_and_shows_author(self):
        author = self.client_for("author@example.com")
        self.assertEqual(self.create_post(author).status_code, 302)

        anon = self.client_for()
        self.assertNotIn("Gara in Giappone", anon.get("/blog/").get_data(as_text=True))
        self.assertEqual(anon.get("/blog/1").status_code, 404)
        self.assertEqual(self.client_for("other@example.com").get("/blog/1").status_code, 404)
        self.assertEqual(author.get("/blog/1").status_code, 200)
        self.assertEqual(author.post("/blog/1/verify").status_code, 403)

        self.assertEqual(self.client_for("admin@example.com").post("/blog/1/verify").status_code, 302)
        self.assertIn("Gara in Giappone", anon.get("/blog/").get_data(as_text=True))
        page = anon.get("/blog/1").get_data(as_text=True)
        self.assertIn("Gianni Verdi", page)
        self.assertIn("<figcaption>didascalia</figcaption>", page)

    def test_photos_use_their_own_folder_and_are_private_until_verified(self):
        self.create_post(self.client_for("author@example.com"))
        with self.app.app_context():
            post = db.session.get(BlogPost, 1)
            image = post.images[0]
            photo_url = f"/media/blog/1/{image.filename}"
            cover_url = f"/media/{post.cover_key}"
            self.assertTrue((Path(self.upload_dir.name) / "blog" / "1" / image.filename).is_file())
        self.assertEqual(self.client_for().get(photo_url).status_code, 404)
        self.assertEqual(self.client_for("author@example.com").get(photo_url).status_code, 200)

        self.client_for("admin@example.com").post("/blog/1/verify")
        anon = self.client_for()
        self.assertEqual(anon.get(photo_url).status_code, 200)
        self.assertEqual(anon.get(cover_url).status_code, 200)
        self.assertIn(f'src="{photo_url}"', anon.get("/blog/1").get_data(as_text=True))

    def test_admin_posts_are_published_immediately(self):
        self.create_post(self.client_for("admin@example.com"))
        self.assertEqual(self.client_for().get("/blog/1").status_code, 200)

    def test_images_are_validated_and_downscaled(self):
        bad = self.create_post(
            self.client_for("author@example.com"),
            photos=[(io.BytesIO(b"<script>"), "evil.png")],
        )
        self.assertEqual(bad.status_code, 200)
        with self.app.app_context():
            self.assertEqual(BlogPost.query.count(), 0)
        self.assertFalse((Path(self.upload_dir.name) / "blog").exists())

        self.create_post(
            self.client_for("author@example.com"),
            photos=[(io.BytesIO(png_bytes((3000, 2000))), "big.png")],
        )
        with self.app.app_context():
            image = db.session.get(BlogPost, 1).images[0]
            with Image.open(Path(self.upload_dir.name) / "blog" / "1" / image.filename) as stored:
                self.assertLessEqual(max(stored.size), 1600)

    def test_delete_permissions_and_cleanup(self):
        author = self.client_for("author@example.com")
        self.create_post(author)
        folder = Path(self.upload_dir.name) / "blog" / "1"
        self.assertEqual(self.client_for("other@example.com").post("/blog/1/delete").status_code, 403)
        self.assertEqual(author.post("/blog/1/delete").status_code, 302)
        self.assertFalse(folder.exists())
        with self.app.app_context():
            self.assertEqual(BlogImage.query.count(), 0)

    def test_index_shows_latest_chapter_in_the_book_and_home_links_to_blog(self):
        self.assertIn("/blog/", self.client_for().get("/").get_data(as_text=True))
        empty = self.client_for().get("/blog/").get_data(as_text=True)
        self.assertNotIn('id="bookOpen"', empty)

        self.create_post(self.client_for("admin@example.com"), text="Abbiamo **caricato** il furgone " + "parola " * 80)
        page = self.client_for().get("/blog/").get_data(as_text=True)
        self.assertIn('id="bookOpen"', page)
        self.assertIn("Gara in Giappone", page)
        self.assertIn("a cura di Gianni V.", page)
        self.assertIn("Abbiamo caricato il furgone", page)
        self.assertIn("(…)", page)
        self.assertNotIn("**", page)

    def test_book_chapter_navigation(self):
        admin = self.client_for("admin@example.com")
        for title in ("Primo", "Secondo", "Terzo"):
            self.create_post(admin, title=title)
        anon = self.client_for()
        default = anon.get("/blog/").get_data(as_text=True)
        self.assertIn("Capitolo 1 di 3", default)
        self.assertIn("Terzo", default.split('id="bookOpen"')[1].split("book-nav")[0])
        self.assertIn("capitolo=2", default)
        self.assertNotIn("capitolo=0", default)
        last = anon.get("/blog/?capitolo=3").get_data(as_text=True)
        self.assertIn("Capitolo 3 di 3", last)
        self.assertIn("Primo", last.split('id="bookOpen"')[1].split("book-nav")[0])
        self.assertNotIn("capitolo=4", last)
        self.assertIn("Capitolo 3 di 3", anon.get("/blog/?capitolo=99").get_data(as_text=True))
        self.assertIn("Capitolo 1 di 3", anon.get("/blog/?capitolo=0").get_data(as_text=True))

    def test_image_size_from_title_and_preview(self):
        self.create_post(
            self.client_for("admin@example.com"),
            text='![a](Foto Uno.PNG "piccola")\n\n![b](Foto Uno.PNG "40%")\n\n![c](Foto Uno.PNG "boh")\n\n![d](Foto Uno.PNG)',
        )
        page = self.client_for().get("/blog/1").get_data(as_text=True)
        self.assertIn('width="50%"', page)
        self.assertIn('width="40%"', page)
        article = page.split("news-article")[1].split("</article>")[0]
        self.assertEqual(article.count("width="), 2)

        client = self.client_for("author@example.com")
        response = client.post(
            "/blog/preview",
            data={
                "title": "Bozza",
                "text": '![x](Foto Uno.PNG "media")\n\n![y](mancante.jpg)',
                "photo_names": '["foto uno.png"]',
                "has_cover": "1",
            },
        )
        data = response.get_json()
        self.assertIn('src="#photo-0"', data["html"])
        self.assertIn('width="70%"', data["html"])
        self.assertIn("Bozza", data["html"])
        self.assertIn('id="previewCover"', data["html"])
        self.assertEqual(data["missing"], ["mancante.jpg"])
        with self.app.app_context():
            self.assertEqual(BlogPost.query.count(), 1)
        self.assertEqual(self.client_for().post("/blog/preview").status_code, 302)

    def test_pending_is_admin_only(self):
        self.assertEqual(self.client_for("author@example.com").get("/blog/pending").status_code, 403)
        self.assertEqual(self.client_for("admin@example.com").get("/blog/pending").status_code, 200)
        self.assertEqual(self.client_for("author@example.com").get("/blog/mine").status_code, 200)


if __name__ == "__main__":
    unittest.main()
