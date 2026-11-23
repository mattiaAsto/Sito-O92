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
    
    # Initialize parametrization (load from Python files if needed)
    from app.parametrization.initialization import initialize_parametrization
    initialize_parametrization(app)

    from app.admin import admin_bp as admin_blueprint
    from app.auth import auth
    from app.blog import blog
    from app.calendar import calendar, routes as calendar_routes
    from app.main import main
    from app.media import media
    from app.news import news
    from app.photos import photos
    from app.shop import shop
    from app.storage import init_storage, media_url
    from app.user import user
    from app.vans import vans

    init_storage(app)
    app.jinja_env.globals["media_url"] = media_url

    app.register_blueprint(main)
    app.register_blueprint(calendar)
    app.register_blueprint(media)
    app.register_blueprint(blog, url_prefix="/blog")
    app.register_blueprint(news, url_prefix="/news")
    app.register_blueprint(photos, url_prefix="/photos")
    app.register_blueprint(shop)
    app.register_blueprint(vans)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(admin_blueprint, url_prefix="/panel")

    from app.models import User
    
    # Import all parametrization models for database registration
    from app.parametrization import (
        Activity, Discipline, CommitteeMember, OtherRole, Monitor, Contact,
        LinkGroup, Link, Club, Sponsor, Document, DocumentMapping,
        Setting, ShopMaterial, ShopMaterialPrice, ShopMaterialSize,
        CalendarCategory
    )

    from app.markdown_render import (
        plain_excerpt,
        render_blog_markdown,
        render_preview_markdown,
        render_text_markdown,
    )

    app.jinja_env.filters["excerpt"] = plain_excerpt
    app.jinja_env.filters["news_markdown"] = render_text_markdown
    app.jinja_env.filters["blog_markdown"] = render_blog_markdown
    app.jinja_env.filters["blog_preview"] = render_preview_markdown

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
    @app.errorhandler(413)
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
