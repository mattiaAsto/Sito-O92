import tempfile
import unittest
import zipfile
from datetime import datetime
from pathlib import Path

from EXPORT import export_site
from app import create_app
from app.extensions import db
from app.models import CalendarActivity


class StaticExportTestCase(unittest.TestCase):
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
        db.session.add(
            CalendarActivity(
                activity_type="attivita",
                category="other_activity",
                title="Static export activity",
                starts_at=datetime(2026, 11, 4, 18),
                ends_at=datetime(2026, 11, 4, 19),
            )
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_export_contains_linked_pages_assets_and_static_calendar_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "preview.zip"
            export_site(self.app, archive_path)

            with zipfile.ZipFile(archive_path) as archive:
                names = set(archive.namelist())
                home = archive.read("index.html").decode("utf-8")
                calendar = archive.read("calendar/index.html").decode("utf-8")

            self.assertIn("links/index.html", home)
            self.assertIn("static/main/css/style.css", names)
            self.assertIn("Static export activity", calendar)
            self.assertIn("staticEvents !== null", calendar)
            self.assertIn("activity/0/index.html", calendar)
