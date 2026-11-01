from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

from app.auth.forms import ItalianForm


class ContactForm(ItalianForm):
    name = StringField(
        "Nome e cognome",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Length(max=100)],
    )
    email = StringField(
        "E-mail",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    message = TextAreaField(
        "Messaggio",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Length(max=5000)],
    )
    submit = SubmitField("Invia")
