import unittest
from datetime import date, timedelta
from unittest.mock import patch

from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import User, VanBooking


class VansTestCase(unittest.TestCase):
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
            for email, flags in (
                ("manager@example.com", {"is_van_manager": True}),
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

    def client_for(self, email=None):
        client = self.app.test_client()
        if email:
            client.post("/auth/login", data={"email": email, "password": "password123"})
        return client

    def booking_data(self, **overrides):
        today = date.today()
        data = {
            "book-van": "trafic",
            "book-start_date": today.isoformat(),
            "book-end_date": (today + timedelta(days=2)).isoformat(),
            "book-note": "",
        }
        data.update(overrides)
        return data

    def test_page_is_public_and_shows_booking(self):
        with self.app.app_context():
            db.session.add(
                VanBooking(van="vivaro", start_date=date.today(), end_date=date.today())
            )
            db.session.commit()
        response = self.client_for().get("/vans")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Opel Vivaro", response.get_data(as_text=True))
        self.assertIn("non disponibile", response.get_data(as_text=True))
        self.assertNotIn("Gestione occupazione", response.get_data(as_text=True))

    def test_only_managers_and_admins_can_add_without_verification(self):
        self.assertEqual(
            self.client_for().post("/vans/occupancy", data=self.booking_data()).status_code,
            302,
        )
        self.assertEqual(
            self.client_for("user@example.com")
            .post("/vans/occupancy", data=self.booking_data())
            .status_code,
            403,
        )
        for email in ("manager@example.com", "admin@example.com"):
            response = self.client_for(email).post(
                "/vans/occupancy", data=self.booking_data()
            )
            self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count(VanBooking.id))), 2)

    def test_invalid_range_rejected(self):
        today = date.today()
        response = self.client_for("manager@example.com").post(
            "/vans/occupancy",
            data=self.booking_data(**{"book-end_date": (today - timedelta(days=1)).isoformat()}),
        )
        self.assertEqual(response.status_code, 400)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count(VanBooking.id))), 0)

    def test_manager_can_delete_but_user_cannot(self):
        with self.app.app_context():
            booking = VanBooking(van="trafic", start_date=date.today(), end_date=date.today())
            db.session.add(booking)
            db.session.commit()
            booking_id = booking.id
        url = f"/vans/occupancy/{booking_id}/delete"
        self.assertEqual(self.client_for("user@example.com").post(url).status_code, 403)
        self.assertEqual(self.client_for("manager@example.com").post(url).status_code, 302)
        with self.app.app_context():
            self.assertIsNone(db.session.get(VanBooking, booking_id))

    def test_rental_request_sends_email(self):
        today = date.today()
        data = {
            "rent-email": "x@example.com",
            "rent-phone_prefix": "079",
            "rent-phone_number": "123 45 67",
            "rent-start_date": today.isoformat(),
            "rent-end_date": today.isoformat(),
            "rent-message": "ciao",
        }
        with patch("app.vans.routes.send_email") as send:
            response = self.client_for().post("/vans", data=data)
        self.assertEqual(response.status_code, 302)
        send.assert_called_once()
        self.assertEqual(send.call_args.kwargs["reply_to"], "x@example.com")

    def test_rental_request_validation(self):
        with patch("app.vans.routes.send_email") as send:
            response = self.client_for().post("/vans", data={"rent-email": "bad"})
        self.assertEqual(response.status_code, 200)
        send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
