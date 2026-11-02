from flask import Blueprint, abort, send_from_directory
from flask_login import current_user

from app.extensions import db
from app.storage import get_storage

media = Blueprint("media", __name__)


def _is_admin_or(condition):
    return current_user.is_authenticated and (current_user.is_admin or condition)


def _can_view(key):
    """Photos of unverified items are only visible to the people who may review them."""
    from app.models import BlogPost, News, Product

    parts = key.split("/")
    try:
        owner_id = int(parts[1])
    except (IndexError, ValueError):
        return False

    if parts[0] == "blog":
        post = db.session.get(BlogPost, owner_id)
        if post is None:
            return False
        return post.is_verified or _is_admin_or(current_user.get_id() == str(post.author_id))
    if parts[0] == "news":
        article = db.session.get(News, owner_id)
        if article is None:
            return False
        return article.is_verified or _is_admin_or(
            current_user.is_authenticated and current_user.is_news_manager
        )
    if parts[0] == "shop":
        product = db.session.get(Product, owner_id)
        if product is None:
            return False
        return product.is_verified or _is_admin_or(
            current_user.get_id() == str(product.seller_id)
        )
    return True


@media.route("/media/<path:key>")
def serve(key):
    if not _can_view(key):
        abort(404)
    path = get_storage().path(key)
    if path is None or not path.is_file():
        abort(404)
    # File names are random and never reused, so public files can be cached for long.
    return send_from_directory(path.parent, path.name, max_age=86400 * 30)
