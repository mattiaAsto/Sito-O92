import unittest

from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import User


class UserTestCase(unittest.TestCase):
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
            }
        )
        with self.app.app_context():
            db.create_all()
            for email in ("a@example.com", "b@example.com"):
                u = User(first_name="A", last_name="B", email=email, is_news_manager=True)
                u.set_password("password123")
                db.session.add(u)
            db.session.commit()
        self.client = self.app.test_client()
        self.client.post(
            "/auth/login", data={"email": "a@example.com", "password": "password123"}
        )

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_requires_login(self):
        response = self.app.test_client().get("/user/")
        self.assertEqual(response.status_code, 302)

    def test_profile_shows_permissions(self):
        response = self.client.get("/user/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Gestore news", response.data)

    def test_edit_profile(self):
        self.client.post(
            "/user/edit",
            data={"first_name": "Mario", "last_name": "Rossi", "email": "New@Example.com"},
        )
        with self.app.app_context():
            u = User.query.filter_by(email="new@example.com").one()
            self.assertEqual(u.first_name, "Mario")

    def test_edit_duplicate_email(self):
        response = self.client.post(
            "/user/edit",
            data={"first_name": "A", "last_name": "B", "email": "b@example.com"},
        )
        self.assertIn("Esiste già".encode(), response.data)

    def test_change_password(self):
        data = {
            "current_password": "wrong",
            "new_password": "newpassword1",
            "confirm_password": "newpassword1",
        }
        self.client.post("/user/password", data=data)
        with self.app.app_context():
            u = User.query.filter_by(email="a@example.com").one()
            self.assertTrue(u.check_password("password123"))
        data["current_password"] = "password123"
        self.client.post("/user/password", data=data)
        with self.app.app_context():
            u = User.query.filter_by(email="a@example.com").one()
            self.assertTrue(u.check_password("newpassword1"))


if __name__ == "__main__":
    unittest.main()
