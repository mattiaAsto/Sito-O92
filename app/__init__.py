import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template

from app.extensions import admin, cache, csrf, db, login_manager, mail, migrate


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    from app.config import Config

    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY in the environment or application config.")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    mail.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    admin.init_app(app)

    from app.auth import auth
    from app.main import main

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def handle_http_error(error):
        if error.code == 500:
            db.session.rollback()
        return (
            render_template(
                "errors/error.html",
                error_code=error.code,
                error_name=error.name,
            ),
            error.code,
        )

    return app
