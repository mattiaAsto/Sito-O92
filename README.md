# Flask application template

A reusable Flask starter based on the application-factory and extension patterns used in fantaCO and TrainingLows. It includes generic session authentication, email support, SQLAlchemy, migrations, CSRF protection, caching, and Flask-Admin. Business-specific routes, data, and branding are intentionally left out.

## Get started

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `SECRET_KEY` in `.env` to a unique random value before starting the app. For example, generate one with:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the development server with `python run.py`, or use `wsgi:app` with a WSGI server. The default database is SQLite at `instance/app.db`; set `DB_COMPLETE_URL` (or `DATABASE_URL`) to use another SQLAlchemy-supported database and install its driver (PyMySQL is included). `python run.py` drops and recreates all tables on every start, then seeds the default test user and 20 sample calendar activities (early development only).

## Project structure

```text
app/
  auth/
    templates/auth/  Login and registration pages
    static/css/      Authentication styles
  calendar/
    templates/calendar/  Calendar page and activity detail page
    palette.py           Activity categories, labels and colors
    routes.py            /calendar, /calendar/events (JSON), /calendar/activity/<id>
    services.py          Shared calendar queries
  main/
    templates/main/  Shared layout and home page
    static/css/      Main application styles
  templates/errors/  App-level HTTP error page
  config.py          Environment-based configuration
  extensions.py
  models.py   User, calendar activity, and shop Product models
  email.py    Reusable Flask-Mail helper
tests/        Standard-library unittest coverage
```

`create_app()` initializes extensions and registers blueprints without creating or changing database tables. Use Flask-Migrate for schema changes:

```sh
flask --app wsgi:app db init
flask --app wsgi:app db migrate -m "describe schema change"
flask --app wsgi:app db upgrade
```

Run tests with `python -m unittest discover -s tests`.

## Static preview export

To package the current public pages and their local assets for a visual review, run:

```sh
python EXPORT.py
```

This creates `site-preview.zip` in the project directory. Choose another destination with
`python EXPORT.py --output path/to/preview.zip`. Extract the archive and open `index.html`;
the exported calendar includes its current activity data. Forms and other server-dependent
features are visual-only, and third-party fonts/icons/framework assets still require internet access.

## Extensions

Import shared extensions from `app.extensions`. SQLAlchemy and Flask-Migrate manage database access and migrations; Flask-Login provides session authentication; Flask-WTF enables CSRF protection; Flask-Mail and Flask-Caching are initialized and configurable. Flask-Admin is initialized without model views; add views only after implementing an authorization policy for them.

Configure SMTP with `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS` or `MAIL_USE_SSL`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_DEFAULT_SENDER`. The `send_email` helper sends mail through the configured Flask-Mail extension.

Registration and login are intentionally small examples. Replace or extend them with the account lifecycle and authorization rules your application requires.

Calendar activities are stored in `calendar_activities` with a type (`allenamento`, `gara`, or `attivita`), a palette category, title, optional description and location, optional latitude/longitude (both or neither; shown as a Google Maps embed on the detail page), and start/end datetimes. The `/calendar` page fetches the visible month from `/calendar/events?start=YYYY-MM-DD&end=YYYY-MM-DD` as JSON and links each activity to `/calendar/activity/<id>`. Palette categories (`app/calendar/palette.py`: Wednesday/Friday trainings, Ticino/Switzerland races, other activities, camps) determine activity labels and colors, and each category is tied to one type by a database constraint. Dates are shown by type: trainings show date and hours, races only the date, and other activities and camps show both dates and times. `app.calendar.services.get_calendar_activities(start_at, end_at)` is the shared query for other blueprints that need calendar data.

## Uploaded images

Uploads go through `app/storage.py`. Every image is validated by its real content, re-encoded (metadata removed, max 1600 px) and saved under `<feature>/<owner id>/<random name>`, for example `news/12/3f2a….jpg`, so files can never overwrite each other. Locally they live in `instance/uploads/` (`UPLOAD_FOLDER`) and are served by `app/media.py`; photos of unverified news are only visible to admins and news managers, photos of unverified shop listings (`shop/<product id>`) only to the seller and admins. The storage interface (`save`, `delete_prefix`, `url`) is backend-agnostic: for deployment on a host with an ephemeral disk, add an S3/Cloudflare R2 backend in `app/storage.py` and select it with `STORAGE_BACKEND`. Use the same `prefix/<id>` convention for new features, e.g. `shop/<product id>`.
