from flask import Blueprint


# Photos are handled by app.storage under the "blog/<id>/" prefix.
blog = Blueprint("blog", __name__, template_folder="templates")

from app.blog import routes
