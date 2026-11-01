import shutil

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()


def create_test_user():
    # Testing only: never ship this account with a real database.
    user = User(
        first_name="Test",
        last_name="Admin",
        email="1@admin.com",
        is_admin=True,
        is_photo_manager=True,
        is_van_manager=True,
        is_news_manager=True,
    )
    user.set_password("12345678")
    db.session.add(user)
    db.session.commit()


def reset_database():
    # Early development only: wipe and rebuild every table (and local uploads) on each start.
    with app.app_context():
        db.drop_all()
        db.create_all()
        if app.config["STORAGE_BACKEND"] == "local":
            shutil.rmtree(app.config["UPLOAD_FOLDER"], ignore_errors=True)
        create_test_user()


if __name__ == "__main__":
    reset_database()

    # Development server: reload templates and refresh the browser on file changes.
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True

    from livereload import Server

    server = Server(app.wsgi_app)
    for pattern in ("app/**/templates/**/*.html", "app/**/static/**/*.css", "app/**/static/**/*.js"):
        server.watch(pattern)
    # Python changes restart the process (debug autoreload); once the browser's
    # livereload client reconnects to the new process, tell it to refresh.
    from livereload.handlers import LiveReloadHandler
    from tornado.ioloop import IOLoop

    def refresh_after_restart(attempts_left=60):
        if LiveReloadHandler.waiters:
            LiveReloadHandler.reload_waiters()
        elif attempts_left:
            IOLoop.current().call_later(0.5, refresh_after_restart, attempts_left - 1)

    IOLoop.current().call_later(0.5, refresh_after_restart)
    server.serve(port=5000, debug=True)
