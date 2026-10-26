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

Start the development server with `python run.py`, or use `wsgi:app` with a WSGI server. The default database is SQLite at `instance/app.db`; set `DATABASE_URL` to use another SQLAlchemy-supported database and install its driver.

## Project structure

```text
app/
  auth/
    templates/auth/  Login and registration pages
    static/css/      Authentication styles
  main/
    templates/main/  Shared layout and home page
    static/css/      Main application styles
  templates/errors/  App-level HTTP error page
  config.py          Environment-based configuration
  extensions.py
  models.py   Starter User model
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

## Extensions

Import shared extensions from `app.extensions`. SQLAlchemy and Flask-Migrate manage database access and migrations; Flask-Login provides session authentication; Flask-WTF enables CSRF protection; Flask-Mail and Flask-Caching are initialized and configurable. Flask-Admin is initialized without model views; add views only after implementing an authorization policy for them.

Configure SMTP with `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS` or `MAIL_USE_SSL`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_DEFAULT_SENDER`. The `send_email` helper sends mail through the configured Flask-Mail extension.

Registration and login are intentionally small examples. Replace or extend them with the account lifecycle and authorization rules your application requires.
