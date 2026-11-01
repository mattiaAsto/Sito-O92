from flask import Blueprint


shop = Blueprint("shop", __name__, template_folder="templates")

from app.shop import routes
