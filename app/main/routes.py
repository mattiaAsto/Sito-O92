from flask import render_template
from flask_login import current_user

from app.main import main


@main.route("/")
def index():
    return render_template("main/index.html", user=current_user)
