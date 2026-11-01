from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.meta import DefaultMeta
from wtforms.validators import DataRequired, Email, EqualTo, Length


class ItalianForm(FlaskForm):
    class Meta(FlaskForm.Meta):
        locales = ["it"]

        def get_translations(self, form):
            # Flask-WTF would otherwise pick its own (English) translations
            return DefaultMeta.get_translations(self, form)


class LoginForm(ItalianForm):
    email = StringField(
        "Email",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Ricordami")
    submit = SubmitField("Accedi")


class RegistrationForm(ItalianForm):

    first_name = StringField(
        "Nome",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Length(max=30)],
    )
    last_name = StringField(
        "Cognome",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Length(max=30)],
    )
    email = StringField(
        "Email",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    confirm_password = PasswordField(
        "Conferma password",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Registrati")
