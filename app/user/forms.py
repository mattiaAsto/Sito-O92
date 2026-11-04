from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.auth.forms import ItalianForm


def _strip(value):
    return value.strip() if value else value


class ProfileForm(ItalianForm):
    first_name = StringField(
        "Nome", filters=[_strip], validators=[DataRequired(), Length(max=30)]
    )
    last_name = StringField(
        "Cognome", filters=[_strip], validators=[DataRequired(), Length(max=30)]
    )
    email = StringField(
        "Email",
        filters=[_strip],
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    submit = SubmitField("Salva modifiche")


class ChangePasswordForm(ItalianForm):
    current_password = PasswordField("Password attuale", validators=[DataRequired()])
    new_password = PasswordField(
        "Nuova password", validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        "Conferma nuova password",
        validators=[DataRequired(), EqualTo("new_password")],
    )
    submit = SubmitField("Cambia password")
