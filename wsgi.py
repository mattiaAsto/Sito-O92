import os

from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()

ADMIN_EMAIL = "webmaster@o-92.ch"


def ensure_admin():
    """Create the admin account from ADMIN_PSWD if it does not exist yet."""
    password = os.getenv("ADMIN_PSWD")
    if not password:
        return
    with app.app_context():
        try:
            if User.query.filter_by(email=ADMIN_EMAIL).first():
                return
            user = User(
                first_name="Admin",
                last_name="Admin",
                email=ADMIN_EMAIL,
                is_admin=True,
                is_photo_manager=True,
                is_van_manager=True,
                is_news_manager=True,
                is_calendar_manager=True,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            # Tables missing yet, or another worker created it first.
            db.session.rollback()


ensure_admin()
