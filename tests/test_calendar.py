import unittest
from datetime import date, datetime, timedelta

from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import CalendarActivity, User


class CalendarManagementTestCase(unittest.TestCase):
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
                ("manager@example.com", {"is_calendar_manager": True}),
                ("admin@example.com", {"is_admin": True}),
                ("user@example.com", {}),
            ):
                user = User(first_name="A", last_name="B", email=email, **flags)
                user.set_password("password123")
                db.session.add(user)
            starts = datetime.now() + timedelta(days=30)
            db.session.add(
                CalendarActivity(
                    activity_type="gara",
                    category="race_ticino",
                    title="Gara esistente",
                    starts_at=starts,
                    ends_at=starts + timedelta(hours=3),
                )
            )
            db.session.commit()
            self.activity_id = db.session.execute(db.select(CalendarActivity.id)).scalar_one()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def client_for(self, email=None):
        client = self.app.test_client()
        if email:
            client.post("/auth/login", data={"email": email, "password": "password123"})
        return client

    def form_data(self, **overrides):
        start = datetime.now() + timedelta(days=10)
        data = {
            "category": "race_switzerland",
            "title": "Nuova gara",
            "starts_at": start.strftime("%Y-%m-%dT%H:%M"),
            "ends_at": (start + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M"),
            "location": "Aarau",
            "latitude": "47.39",
            "longitude": "8.04",
            "description": "",
            "inscription_delay_date": (date.today() + timedelta(days=5)).isoformat(),
            "weekly_repeats": "1",
        }
        data.update(overrides)
        return data

    def count(self):
        with self.app.app_context():
            return len(db.session.execute(db.select(CalendarActivity)).scalars().all())

    def test_calendar_manager_flag_defaults_to_false(self):
        with self.app.app_context():
            user = db.session.execute(db.select(User).filter_by(email="user@example.com")).scalar_one()
            self.assertFalse(user.is_calendar_manager)

    def test_controls_are_only_visible_to_managers_and_admins(self):
        detail = f"/calendar/activity/{self.activity_id}"
        for email, visible in (
            ("manager@example.com", True),
            ("admin@example.com", True),
            ("user@example.com", False),
            (None, False),
        ):
            client = self.client_for(email)
            page = client.get("/calendar").get_data(as_text=True)
            info = client.get(detail).get_data(as_text=True)
            self.assertEqual("/calendar/activity/new" in page, visible, email)
            self.assertEqual("Elimina attività" in info, visible, email)

    def test_only_managers_can_create_edit_and_delete(self):
        for email, status in (("user@example.com", 403), (None, 302)):
            client = self.client_for(email)
            self.assertEqual(client.get("/calendar/activity/new").status_code, status)
            self.assertEqual(client.post("/calendar/activity/new", data=self.form_data()).status_code, status)
            self.assertEqual(client.post(f"/calendar/activity/{self.activity_id}/delete").status_code, status)
        self.assertEqual(self.count(), 1)

    def test_manager_creates_activity_and_type_follows_category(self):
        response = self.client_for("manager@example.com").post(
            "/calendar/activity/new", data=self.form_data()
        )
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            created = db.session.execute(
                db.select(CalendarActivity).filter_by(title="Nuova gara")
            ).scalar_one()
            self.assertEqual(created.activity_type, "gara")
            self.assertIsNotNone(created.inscription_delay_date)

    def test_weekly_training_series_and_no_delay_for_trainings(self):
        response = self.client_for("admin@example.com").post(
            "/calendar/activity/new",
            data=self.form_data(
                category="training_friday", title="Serie", weekly_repeats="4",
                inscription_delay_date="",
            ),
        )
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            series = db.session.execute(
                db.select(CalendarActivity)
                .filter_by(title="Serie")
                .order_by(CalendarActivity.starts_at)
            ).scalars().all()
            self.assertEqual(len(series), 4)
            self.assertEqual(series[1].starts_at - series[0].starts_at, timedelta(weeks=1))

    def test_invalid_submissions_are_rejected(self):
        client = self.client_for("manager@example.com")
        for overrides in (
            {"ends_at": "2000-01-01T00:00"},
            {"latitude": ""},
            {"category": "training_friday"},
            {"inscription_delay_date": (date.today() + timedelta(days=99)).isoformat()},
            {"category": "race_ticino", "weekly_repeats": "3"},
        ):
            response = client.post("/calendar/activity/new", data=self.form_data(**overrides))
            self.assertEqual(response.status_code, 400, overrides)
        self.assertEqual(self.count(), 1)

    def test_manager_edits_and_deletes_activity(self):
        client = self.client_for("manager@example.com")
        response = client.post(
            f"/calendar/activity/{self.activity_id}/edit",
            data=self.form_data(title="Titolo modificato"),
        )
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            self.assertEqual(
                db.session.get(CalendarActivity, self.activity_id).title, "Titolo modificato"
            )

        self.assertEqual(
            client.post(f"/calendar/activity/{self.activity_id}/delete").status_code, 302
        )
        self.assertEqual(self.count(), 0)
        self.assertEqual(client.post(f"/calendar/activity/{self.activity_id}/delete").status_code, 404)


if __name__ == "__main__":
    unittest.main()
