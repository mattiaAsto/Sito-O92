"""Sync the database schema with app/models.py.

Creates missing tables and adds missing columns. It never drops or alters
anything, so it is safe to run on every deploy.

Dry run:  python production_update.py
Apply:    APP_ENV=production python production_update.py --apply --yes
"""
import argparse
import sys

from sqlalchemy import inspect, text
from sqlalchemy.schema import CreateColumn

from app import create_app
from app.extensions import db


def plan():
    inspector = inspect(db.engine)
    existing = set(inspector.get_table_names())
    new_tables, new_columns = [], []
    for table in db.metadata.sorted_tables:
        if table.name not in existing:
            new_tables.append(table.name)
            continue
        present = {c["name"] for c in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name not in present:
                new_columns.append((table, column))
    return new_tables, new_columns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="execute the changes")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        new_tables, new_columns = plan()
        print(f"Database: {db.engine.url.render_as_string(hide_password=True)}")
        for name in new_tables:
            print(f"  + table  {name}")
        for table, column in new_columns:
            print(f"  + column {table.name}.{column.name}")
        if not new_tables and not new_columns:
            print("Schema already up to date.")
            return 0
        if not args.apply:
            print("Dry run: nothing changed. Use --apply to execute.")
            return 0
        if not args.yes and input("Apply these changes? [y/N] ").lower() != "y":
            print("Aborted.")
            return 1

        db.create_all()
        with db.engine.begin() as conn:
            for table, column in new_columns:
                ddl = CreateColumn(column).compile(dialect=db.engine.dialect)
                conn.execute(text(f"ALTER TABLE {table.name} ADD COLUMN {ddl}"))
        print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
