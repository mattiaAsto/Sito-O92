from flask import Blueprint


# Photos are handled by app.storage under the "news/<id>/" prefix.
news = Blueprint("news", __name__, template_folder="templates")

from app.news import routes
