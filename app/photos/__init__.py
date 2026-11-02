from flask import Blueprint


# Albums and photos mirror the Dropbox folder; images are proxied from Dropbox, never stored here.
photos = Blueprint("photos", __name__, template_folder="templates")

from app.photos import routes
