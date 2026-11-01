import unittest
from decimal import Decimal
from unittest.mock import patch

from app import create_app
from app.email import send_email
from app.extensions import db
from app.models import Product, User


class ApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "WTF_CSRF_ENABLED": False,
            }
        )
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_and_auth_pages_render(self):
        home = self.client.get("/")
        login = self.client.get("/auth/login")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"/static/main/css/style.css", home.data)
        self.assertEqual(login.status_code, 200)
        self.assertIn(b"/auth/static/css/forms.css", login.data)
        self.assertEqual(self.client.get("/auth/register").status_code, 200)

    def test_shop_uses_its_own_blueprint_and_main_layout(self):
        empty_response = self.client.get("/shop")

        self.assertEqual(empty_response.status_code, 200)
        self.assertIn("shop", self.app.blueprints)
        self.assertIn(b"/static/main/css/style.css", empty_response.data)
        self.assertIn(b'href="/shop"', empty_response.data)
        self.assertIn(b"Abbigliamento del team", empty_response.data)
        self.assertIn(b"Abbigliamento usato", empty_response.data)

        product = Product(
            name="Maglia da orientamento",
            description="Maglia tecnica della squadra.",
            category="Abbigliamento",
            price=Decimal("49.90"),
        )
        used_product = Product(
            name="Giacca da gara usata",
            description="Giacca in buone condizioni.",
            category="Abbigliamento",
            listing_type="used",
            price=Decimal("20.00"),
        )
        db.session.add_all([product, used_product])
        db.session.commit()

        response = self.client.get("/shop")
        self.assertEqual(response.status_code, 200)
        team_section = response.data.index(b"Abbigliamento del team")
        used_section = response.data.index(b"Abbigliamento usato")
        self.assertLess(team_section, used_section)
        self.assertIn(b"Maglia da orientamento", response.data)
        self.assertIn(b"Giacca da gara usata", response.data)
        self.assertIn(b"CHF 49.90", response.data)
        self.assertNotIn(b"Al momento non ci sono articoli del team", response.data)
        self.assertNotIn(b"Al momento non ci sono capi usati", response.data)

    def test_blueprint_static_assets_and_app_error_page(self):
        with self.client.get("/static/main/css/style.css") as response:
            self.assertEqual(response.status_code, 200)
        with self.client.get("/auth/static/css/forms.css") as response:
            self.assertEqual(response.status_code, 200)

        response = self.client.get("/missing-page")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)
        self.assertIn(b"Return home", response.data)

    def test_registration_and_login(self):
        response = self.client.post(
            "/auth/register",
            data={
                "first_name": "Mario",
                "last_name": "Rossi",
                "email": " Person@Example.com ",
                "password": "correct horse battery",
                "confirm_password": "correct horse battery",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.query.filter_by(email="person@example.com").one()
        self.assertEqual((user.first_name, user.last_name), ("Mario", "Rossi"))
        self.assertIsInstance(user.password, bytes)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.check_password("correct horse battery"))

        response = self.client.post(
            "/auth/login",
            data={
                "email": "PERSON@example.com",
                "password": "correct horse battery",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"Logout", self.client.get("/").data)

    def test_registration_rejects_invalid_password_confirmation(self):
        response = self.client.post(
            "/auth/register",
            data={
                "first_name": "Mario",
                "last_name": "Rossi",
                "email": "person@example.com",
                "password": "correct horse battery",
                "confirm_password": "different password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.query.count(), 0)

    def test_contact_form(self):
        self.assertEqual(self.client.get("/contatti").status_code, 200)
        invalid = self.client.post("/contatti", data={"name": "Mario"})
        self.assertEqual(invalid.status_code, 200)
        with patch("app.main.routes.send_email") as send:
            valid = self.client.post(
                "/contatti",
                data={"name": "Mario", "email": "m@example.com", "message": "Ciao"},
            )
        self.assertEqual(valid.status_code, 302)
        send.assert_called_once()

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get("/auth/logout").status_code, 405)

    def test_csrf_protects_post_routes(self):
        csrf_app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "WTF_CSRF_ENABLED": True,
            }
        )
        self.assertEqual(csrf_app.test_client().post("/auth/login").status_code, 400)

    def test_email_helper_sends_a_message(self):
        with patch("app.email.mail.send") as send:
            send_email("Subject", ["person@example.com"], "Body", "<p>Body</p>")

        message = send.call_args.args[0]
        self.assertEqual(message.subject, "Subject")
        self.assertEqual(message.recipients, ["person@example.com"])
        self.assertEqual(message.body, "Body")
        self.assertEqual(message.html, "<p>Body</p>")


if __name__ == "__main__":
    unittest.main()
