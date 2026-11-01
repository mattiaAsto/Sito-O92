from flask import Blueprint


# Article photos live in app/news/static/<news_id>/ and are served at /news/static/<news_id>/.
news = Blueprint(
    "news",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)

from app.news import routes
