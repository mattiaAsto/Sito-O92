import io
import tempfile
import unittest
from pathlib import Path

from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import Product, User
from tests.test_news import png_bytes


class ShopTestCase(unittest.TestCase):
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
                ("seller@example.com", {}),
                ("other@example.com", {}),
            ):
                user = User(first_name="Sara", last_name="Rossi", email=email, **flags)
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

    def create_product(self, client, photos=1, files=None, **overrides):
        data = {
            "name": "Giacca usata",
            "category": "Giacche",
            "size": "M",
            "price": "25.50",
            "description": "Ottime condizioni",
            "photos": files or [(io.BytesIO(png_bytes()), f"p{i}.png") for i in range(photos)],
        }
        data.update(overrides)
        return client.post("/shop/create", data=data, content_type="multipart/form-data")

    def product(self):
        with self.app.app_context():
            return db.session.execute(db.select(Product)).scalars().first()

    def test_create_requires_login(self):
        self.assertEqual(self.client_for().get("/shop/create").status_code, 302)
        self.assertEqual(self.client_for("seller@example.com").get("/shop/create").status_code, 200)

    def test_listing_needs_admin_verification(self):
        seller = self.client_for("seller@example.com")
        self.assertEqual(self.create_product(seller, photos=2).status_code, 302)
        with self.app.app_context():
            product = db.session.execute(db.select(Product)).scalars().one()
            pid, key = product.id, product.cover_key
            self.assertFalse(product.is_verified)
            self.assertEqual(len(product.images), 2)

        anon = self.client_for()
        self.assertNotIn(b"Giacca usata", anon.get("/shop").data)
        self.assertEqual(anon.get(f"/shop/{pid}").status_code, 404)
        self.assertEqual(anon.get(f"/media/{key}").status_code, 404)
        self.assertEqual(self.client_for("other@example.com").get(f"/shop/{pid}").status_code, 404)
        self.assertEqual(seller.get(f"/shop/{pid}").status_code, 200)
        self.assertEqual(seller.get(f"/media/{key}").status_code, 200)
        self.assertEqual(seller.post(f"/shop/{pid}/verify").status_code, 403)

        admin = self.client_for("admin@example.com")
        self.assertIn(b"Giacca usata", admin.get("/shop/pending").data)
        self.assertEqual(admin.post(f"/shop/{pid}/verify").status_code, 302)

        self.assertIn(b"Giacca usata", anon.get("/shop").data)
        detail = anon.get(f"/shop/{pid}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"seller@example.com", detail.data)
        self.assertEqual(anon.get(f"/media/{key}").status_code, 200)

    def test_official_clothing_is_admin_only(self):
        self.create_product(self.client_for("seller@example.com"), is_official_clothing="y")
        self.assertFalse(self.product().is_official_clothing)

        with self.app.app_context():
            db.session.execute(db.delete(Product))
            db.session.commit()
        admin = self.client_for("admin@example.com")
        self.create_product(admin, name="Maglia team", is_official_clothing="y")
        product = self.product()
        self.assertTrue(product.is_official_clothing)
        self.assertTrue(product.is_verified)
        page = self.client_for().get("/shop").data
        self.assertLess(page.index(b"Maglia team"), page.index(b"Abbigliamento usato</h2>"))

    def test_invalid_image_is_rejected_without_saving(self):
        response = self.create_product(
            self.client_for("seller@example.com"),
            files=[(io.BytesIO(b"not an image"), "x.png")],
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.product())

    def test_sold_toggle_and_delete_permissions(self):
        seller = self.client_for("seller@example.com")
        self.create_product(seller)
        pid = self.product().id
        self.assertEqual(self.client_for("other@example.com").post(f"/shop/{pid}/sold").status_code, 403)
        self.assertEqual(self.client_for("other@example.com").post(f"/shop/{pid}/delete").status_code, 403)

        admin = self.client_for("admin@example.com")
        admin.post(f"/shop/{pid}/verify")
        seller.post(f"/shop/{pid}/sold")
        self.assertNotIn(b"Giacca usata", self.client_for().get("/shop").data)
        self.assertEqual(self.client_for().get(f"/shop/{pid}").status_code, 200)

        folder = Path(self.upload_dir.name) / "shop" / str(pid)
        self.assertTrue(folder.exists())
        seller.post(f"/shop/{pid}/delete")
        self.assertIsNone(self.product())
        self.assertFalse(folder.exists())
