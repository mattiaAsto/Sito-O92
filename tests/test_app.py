import unittest
from unittest.mock import patch

from app import create_app
from app.email import send_email
from app.extensions import db
from app.models import User


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
                "email": " Person@Example.com ",
                "password": "correct horse battery",
                "confirm_password": "correct horse battery",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.query.filter_by(email="person@example.com").one()
        self.assertTrue(user.check_password("correct horse battery"))

        response = self.client.post(
            "/auth/login",
            data={
                "email": "PERSON@example.com",
                "password": "correct horse battery",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            b"You are signed in as person@example.com.",
            self.client.get("/").data,
        )

    def test_registration_rejects_invalid_password_confirmation(self):
        response = self.client.post(
            "/auth/register",
            data={
                "email": "person@example.com",
                "password": "correct horse battery",
                "confirm_password": "different password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.query.count(), 0)

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
