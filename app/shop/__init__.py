from flask import Blueprint


shop = Blueprint(
    "shop",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/shop",
)

from app.shop import routes
