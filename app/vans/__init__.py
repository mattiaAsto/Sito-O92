from flask import Blueprint


vans = Blueprint(
    "vans",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/vans",
)

from app.vans import routes
