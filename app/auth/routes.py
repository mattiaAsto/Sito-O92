from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("main.index"))
        flash("Invalid email or password.", "error")

    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An account with that email already exists.", "error")
        else:
            flash("Your account has been created. Please sign in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("main.index"))
