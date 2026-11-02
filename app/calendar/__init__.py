from flask import Blueprint


calendar = Blueprint(
    "calendar",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/calendar",
)
