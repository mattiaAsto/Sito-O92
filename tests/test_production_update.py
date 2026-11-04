import unittest
from unittest.mock import Mock

from sqlalchemy.dialects import postgresql
from sqlalchemy import text
from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db
from app.models import Album
from production_update import _make_nullable, plan


class ProductionUpdateTestCase(unittest.TestCase):
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
            }
        )
        with self.app.app_context(), db.engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE photo_albums ("
                    "id INTEGER PRIMARY KEY, "
                    "dropbox_path VARCHAR(500) NOT NULL, "
                    "title VARCHAR(255) NOT NULL, "
                    "cover_path VARCHAR(600) NOT NULL, "
                    "is_visible BOOLEAN NOT NULL, "
                    "date DATETIME NOT NULL, "
                    "photos_loaded_at DATETIME)"
                )
            )

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_plan_detects_nullable_model_column_with_stale_not_null_constraint(self):
        with self.app.app_context():
            _, _, nullable_columns = plan()

        self.assertIn(
            ("photo_albums", "cover_path"),
            {(table.name, column.name) for table, column in nullable_columns},
        )

    def test_postgresql_migration_drops_not_null_constraint(self):
        connection = Mock()
        connection.dialect = postgresql.dialect()

        _make_nullable(connection, Album.__table__, Album.__table__.c.cover_path)

        statement = connection.execute.call_args.args[0]
        self.assertEqual(
            statement.text,
            "ALTER TABLE photo_albums ALTER COLUMN cover_path DROP NOT NULL",
        )


if __name__ == "__main__":
    unittest.main()
