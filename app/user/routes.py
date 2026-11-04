from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.user import user
from app.user.forms import ChangePasswordForm, ProfileForm

PERMISSIONS = (
    ("is_admin", "Amministratore", "Accesso completo e verifica dei contenuti."),
    ("is_news_manager", "Gestore news", "Può pubblicare e modificare le news."),
    ("is_photo_manager", "Gestore foto", "Può gestire gli album fotografici."),
    ("is_van_manager", "Gestore furgoni", "Può gestire le prenotazioni dei furgoni."),
    ("is_calendar_manager", "Gestore calendario", "Può creare, modificare ed eliminare le attività del calendario."),
)


def _permissions():
    return [
        {"label": label, "description": description, "granted": getattr(current_user, attr)}
        for attr, label, description in PERMISSIONS
    ]


def _render(profile_form, password_form):
    return render_template(
        "user/profile.html",
        profile_form=profile_form,
        password_form=password_form,
        permissions=_permissions(),
    )


@user.route("/", methods=["GET"])
@login_required
def profile():
    return _render(ProfileForm(obj=current_user), ChangePasswordForm())


@user.route("/edit", methods=["POST"])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data.lower()
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Esiste già un account con questa email.", "error")
        else:
            flash("Dati aggiornati.", "success")
            return redirect(url_for("user.profile"))
    return _render(form, ChangePasswordForm())


@user.route("/password", methods=["POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            form.current_password.errors.append("Password attuale non corretta.")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password aggiornata.", "success")
            return redirect(url_for("user.profile"))
    return _render(ProfileForm(obj=current_user), form)
