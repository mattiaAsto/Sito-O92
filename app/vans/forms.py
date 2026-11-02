from datetime import date

from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, ValidationError

from app.auth.forms import ItalianForm

VANS = {
    "trafic": "Renault Trafic",
    "vivaro": "Opel Vivaro",
}

VAN_COLORS = {
    "trafic": "#8a4b0f",
    "vivaro": "#2f5d8c",
}


def _strip(value):
    return value.strip() if value else value


class _DateRangeForm(ItalianForm):
    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("La data finale non può precedere quella iniziale.")


class RentalRequestForm(_DateRangeForm):
    email = StringField(
        "Email richiedente",
        filters=[_strip],
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    phone_prefix = StringField(
        "Prefisso",
        filters=[_strip],
        validators=[DataRequired(), Regexp(r"^\+?\d{2,5}$", message="Prefisso non valido.")],
    )
    phone_number = StringField(
        "Numero",
        filters=[_strip],
        validators=[DataRequired(), Regexp(r"^[\d ]{5,15}$", message="Numero non valido.")],
    )
    start_date = DateField("Richiesta dal", validators=[DataRequired()])
    end_date = DateField("al", validators=[DataRequired()])
    message = TextAreaField("Messaggio", filters=[_strip], validators=[Length(max=3000)])
    submit = SubmitField("Invia richiesta")

    def validate_start_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("La data iniziale non può essere nel passato.")


class BookingForm(_DateRangeForm):
    van = SelectField("Furgone", choices=list(VANS.items()), validators=[DataRequired()])
    start_date = DateField("Dal", validators=[DataRequired()])
    end_date = DateField("Al", validators=[DataRequired()])
    note = StringField(
        "Nota (visibile solo a chi gestisce)",
        filters=[_strip],
        validators=[Optional(), Length(max=200)],
    )
    submit = SubmitField("Segna non disponibile")
