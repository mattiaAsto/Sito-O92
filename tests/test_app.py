import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from sqlalchemy.exc import IntegrityError

from app import create_app
from app.email import send_email
from app.extensions import db
from app.models import CalendarActivity, Product, User


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
        links = self.client.get("/links")
        self.assertEqual(links.status_code, 200)
        self.assertIn(b"Societ\xc3\xa0 ticinesi", links.data)
        self.assertIn(b"https://www.asco-lugano.ch", links.data)
        self.assertIn(b'href="/links"', home.data)
        self.assertEqual(login.status_code, 200)
        self.assertIn(b"/auth/static/css/forms.css", login.data)
        self.assertEqual(self.client.get("/auth/register").status_code, 200)

    def test_public_routes_use_english_paths(self):
        routes = {rule.rule for rule in self.app.url_map.iter_rules()}
        self.assertTrue(
            {
                "/what-is-orienteering",
                "/training",
                "/races",
                "/activities",
                "/about-us",
                "/gallery",
                "/contact",
                "/calendar",
                "/vans",
                "/vans/occupancy",
                "/vans/occupancy/<int:booking_id>/delete",
            }.issubset(routes)
        )
        self.assertTrue(
            {
                "/whats_orienteering",
                "/allenamenti",
                "/gare",
                "/attivita",
                "/chi-siamo",
                "/foto",
                "/contatti",
                "/calendario",
                "/furgoni",
                "/furgoni/occupazione",
                "/furgoni/occupazione/<int:booking_id>/elimina",
            }.isdisjoint(routes)
        )

    def test_who_we_are_page_links_documents(self):
        response = self.client.get("/about-us")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.count(b'<details class="who-accordion">'), 3)
        self.assertIn(b"<h2 class=\"page-subtitle contact-title\">Documenti</h2>", response.data)
        for document in (
            "statutes_20251017.pdf",
            "regulations_2025.pdf",
            "sports_code_of_ethics.pdf",
            "o92_abc.pdf",
            "sponsorship_2026.pdf",
        ):
            with self.subTest(document=document):
                document_response = self.client.get(
                    f"/static/main/pdf/who_are_we/{document}"
                )
                self.assertEqual(document_response.status_code, 200)
                self.assertIn(document.encode(), response.data)
                document_response.close()

    def test_who_we_are_slideshow_uses_supported_images(self):
        with TemporaryDirectory() as temp_dir:
            slideshow_folder = Path(temp_dir) / "pictures" / "slideshow"
            slideshow_folder.mkdir(parents=True)
            for filename in ("second.jpg", "first.png", "ignored.txt"):
                (slideshow_folder / filename).touch()

            from app.main.routes import get_slideshow_images

            self.assertEqual(
                get_slideshow_images(slideshow_folder),
                ["first.png", "second.jpg"],
            )

        with patch(
            "app.main.routes.get_slideshow_images",
            return_value=["first.png", "second.jpg"],
        ):
            response = self.client.get("/about-us")

        self.assertEqual(response.status_code, 200)
        self.assertLess(response.data.index(b"first.png"), response.data.index(b"second.jpg"))
        self.assertEqual(response.data.count(b'class="carousel-item'), 4)
        self.assertNotIn(b"ignored.txt", response.data)
        self.assertIn(b"data-bs-slide=\"next\"", response.data)
        self.assertIn(b'data-bs-target="#whoSlideshowModal"', response.data)
        self.assertEqual(response.data.count(b'data-bs-interval="3000"'), 2)

    def test_links_page_lists_all_documents(self):
        response = self.client.get("/links")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lista di tutti i documenti", response.data)
        for document in (
            "newcomers_info_2022.pdf",
            "swiss_orienteering_competencies_21.pdf",
            "iof_control_descriptions.pdf",
            "ticks_flyer_ti.pdf",
            "forest_map_legend.pdf",
            "city_map_legend.pdf",
            "o92_abc.pdf",
            "sports_code_of_ethics.pdf",
            "sponsorship_2026.pdf",
            "regulations_2025.pdf",
            "statutes_20251017.pdf",
        ):
            with self.subTest(document=document):
                self.assertIn(document.encode(), response.data)

    def test_races_page_links_to_online_tmo_and_national_registrations(self):
        response = self.client.get("/races")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="https://ol-events.ch"', response.data)
        self.assertIn(b'Iscrizioni online', response.data)

    def test_miscellaneous_pdfs_are_linked_from_their_pages(self):
        documents_by_page = {
            "/what-is-orienteering": (
                "whats_orienteering",
                (
                    "swiss_orienteering_competencies_21.pdf",
                    "iof_control_descriptions.pdf",
                    "forest_map_legend.pdf",
                    "city_map_legend.pdf",
                    "ticks_flyer_ti.pdf",
                ),
            ),
            "/contact": ("contacts", ("newcomers_info_2022.pdf",)),
        }
        for page, (folder, documents) in documents_by_page.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)
                for document in documents:
                    with self.subTest(document=document):
                        self.assertIn(document.encode(), response.data)
                        pdf_response = self.client.get(
                            f"/static/main/pdf/{folder}/{document}"
                        )
                        self.assertEqual(pdf_response.status_code, 200)
                        pdf_response.close()

    def test_shop_uses_its_own_blueprint_and_main_layout(self):
        empty_response = self.client.get("/shop")

        self.assertEqual(empty_response.status_code, 200)
        self.assertIn("shop", self.app.blueprints)
        self.assertIn(b"/static/main/css/style.css", empty_response.data)
        self.assertIn(b'href="/shop"', empty_response.data)
        self.assertIn(b"Abbigliamento del team", empty_response.data)
        self.assertIn(b"Abbigliamento usato", empty_response.data)

        seller = User(email="s@x.ch", first_name="Sara", last_name="Rossi")
        seller.set_password("12345678")
        db.session.add(seller)
        db.session.flush()
        product = Product(
            seller_id=seller.id,
            name="Maglia da orientamento",
            description="Maglia tecnica della squadra.",
            category="Maglie",
            is_official_clothing=True,
            is_verified=True,
            price=Decimal("49.90"),
        )
        used_product = Product(
            seller_id=seller.id,
            name="Giacca da gara usata",
            description="Giacca in buone condizioni.",
            category="Giacche",
            is_verified=True,
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

    def test_calendar_blueprint_loads_activity_data_and_renders_details_route(self):
        activity = CalendarActivity(
            activity_type="gara",
            category="race_ticino",
            title="Gara cantonale",
            description="Prima gara della stagione.",
            starts_at=datetime(2026, 3, 14, 9, 0),
            ends_at=datetime(2026, 3, 14, 15, 0),
            location="Bellinzona",
            latitude=46.1946,
            longitude=9.0244,
        )
        db.session.add(activity)
        db.session.commit()

        page = self.client.get("/calendar")

        self.assertIn("calendar", self.app.blueprints)
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"/calendar/events", page.data)
        self.assertIn(b"fetch(", page.data)

        response = self.client.get(
            "/calendar/events?start=2026-03-01&end=2026-04-01"
        )
        self.assertEqual(response.status_code, 200)
        event = response.json["events"][0]
        self.assertEqual(event["title"], "Gara cantonale")
        self.assertEqual(event["color"], "#64B5F6")
        self.assertEqual(event["category_label"], "Gara - Ticino")
        self.assertIsNone(event["time"])
        self.assertEqual(event["location"], "Bellinzona")

        detail = self.client.get(f"/calendar/activity/{activity.id}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"Gara cantonale", detail.data)
        self.assertIn(b"Gara - Ticino", detail.data)
        self.assertIn(b"maps.google.com/maps?q=46.1946,9.0244", detail.data)
        self.assertEqual(self.client.get("/calendar/activity/9999").status_code, 404)
        self.assertEqual(self.client.get("/calendario").status_code, 404)

    def test_activity_pages_show_five_upcoming_events_of_their_type(self):
        types = {
            "allenamento": ("training_wednesday", "/training", "Prossimi allenamenti"),
            "gara": ("race_ticino", "/races", "Prossime gare"),
            "attivita": ("other_activity", "/activities", "Prossime attività"),
        }
        for activity_type, (category, _, _) in types.items():
            for day in range(1, 7):
                db.session.add(
                    CalendarActivity(
                        activity_type=activity_type,
                        category=category,
                        title=f"{activity_type} 2030-{day}",
                        starts_at=datetime(2030, 1, day, 18, 0),
                        ends_at=datetime(2030, 1, day, 19, 0),
                    )
                )
        db.session.commit()

        for activity_type, (_, path, title) in types.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(title.encode(), response.data)
                self.assertIn(f"{activity_type} 2030-5".encode(), response.data)
                self.assertNotIn(f"{activity_type} 2030-6".encode(), response.data)
                other_types = set(types) - {activity_type}
                for other_type in other_types:
                    self.assertNotIn(other_type.encode() + b" 2030-", response.data)

    def test_calendar_schedule_labels_depend_on_activity_type(self):
        def make(activity_type, category, start, end):
            return CalendarActivity(
                activity_type=activity_type,
                category=category,
                title="x",
                starts_at=start,
                ends_at=end,
            )

        training = make(
            "allenamento", "training_wednesday",
            datetime(2026, 3, 11, 18, 0), datetime(2026, 3, 11, 19, 30),
        )
        race = make(
            "gara", "race_ticino",
            datetime(2026, 3, 14, 9, 0), datetime(2026, 3, 14, 15, 0),
        )
        camp = make(
            "attivita", "camp",
            datetime(2026, 4, 3, 9, 0), datetime(2026, 4, 5, 16, 0),
        )

        self.assertEqual(training.schedule_label, "11.03.2026, 18:00 – 19:30")
        self.assertEqual(training.time_label, "18:00 – 19:30")
        self.assertEqual(race.schedule_label, "14.03.2026")
        self.assertIsNone(race.time_label)
        self.assertEqual(camp.schedule_label, "03.04.2026 09:00 – 05.04.2026 16:00")
        self.assertEqual(camp.time_label, "09:00")

    def test_calendar_activity_without_coordinates_has_no_map(self):
        activity = CalendarActivity(
            activity_type="attivita",
            category="other_activity",
            title="Cena sociale",
            starts_at=datetime(2026, 3, 14, 19, 0),
            ends_at=datetime(2026, 3, 14, 22, 0),
        )
        db.session.add(activity)
        db.session.commit()

        detail = self.client.get(f"/calendar/activity/{activity.id}")

        self.assertEqual(detail.status_code, 200)
        self.assertNotIn(b"<iframe", detail.data)

    def test_calendar_activity_rejects_partial_coordinates(self):
        db.session.add(
            CalendarActivity(
                activity_type="gara",
                category="race_ticino",
                title="Invalid coordinates",
                starts_at=datetime(2026, 3, 14, 9, 0),
                ends_at=datetime(2026, 3, 14, 10, 0),
                latitude=46.0,
            )
        )

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    def test_calendar_events_rejects_invalid_date_range(self):
        response = self.client.get(
            "/calendar/events?start=2026-04-01&end=2026-03-01"
        )

        self.assertEqual(response.status_code, 400)

    def test_home_shows_next_activity_per_type(self):
        from datetime import timedelta

        now = datetime.now()
        db.session.add_all([
            CalendarActivity(activity_type="allenamento", category="training_friday",
                             title="Passato", starts_at=now - timedelta(days=3),
                             ends_at=now - timedelta(days=3, hours=-1)),
            CalendarActivity(activity_type="allenamento", category="training_friday",
                             title="Prossimo allenamento", starts_at=now + timedelta(days=2),
                             ends_at=now + timedelta(days=2, hours=1)),
            CalendarActivity(activity_type="gara", category="race_ticino",
                             title="Prossima gara", starts_at=now + timedelta(days=5),
                             ends_at=now + timedelta(days=5, hours=2)),
        ])
        db.session.commit()

        html = self.client.get("/").get_data(as_text=True)

        self.assertIn("Prossimo allenamento", html)
        self.assertIn("Prossima gara", html)
        self.assertNotIn("Passato", html)
        self.assertIn("Nessuna attività in programma", html)

    def test_calendar_lists_three_upcoming_inscription_deadlines(self):
        from datetime import date, timedelta

        today = date.today()
        starts = datetime.now() + timedelta(days=40)
        for index, delta in enumerate((-2, 9, 3, 6, 1)):
            db.session.add(CalendarActivity(
                activity_type="gara", category="race_ticino",
                title=f"Gara {index}", starts_at=starts, ends_at=starts + timedelta(hours=2),
                inscription_delay_date=today + timedelta(days=delta),
            ))
        db.session.commit()

        html = self.client.get("/calendar").get_data(as_text=True)

        self.assertIn("Prossime scadenze", html)
        self.assertLess(html.index("Gara 4"), html.index("Gara 2"))
        self.assertLess(html.index("Gara 2"), html.index("Gara 3"))
        self.assertNotIn("Gara 0", html)
        self.assertNotIn("Gara 1", html)

    def test_training_cannot_have_inscription_delay(self):
        from datetime import date

        db.session.add(CalendarActivity(
            activity_type="allenamento", category="training_friday", title="T",
            starts_at=datetime(2026, 3, 14, 9, 0), ends_at=datetime(2026, 3, 14, 10, 0),
            inscription_delay_date=date(2026, 3, 10),
        ))
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_calendar_activity_rejects_invalid_category_type(self):
        activity = CalendarActivity(
            activity_type="gara",
            category="training_wednesday",
            title="Invalid activity",
            starts_at=datetime(2026, 3, 14, 9, 0),
            ends_at=datetime(2026, 3, 14, 10, 0),
        )
        db.session.add(activity)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

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
        self.assertEqual(self.client.get("/contact").status_code, 200)
        invalid = self.client.post("/contact", data={"name": "Mario"})
        self.assertEqual(invalid.status_code, 200)
        with patch("app.main.routes.send_email") as send:
            valid = self.client.post(
                "/contact",
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
