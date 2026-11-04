from wtforms import (
    DateField,
    DateTimeLocalField,
    FloatField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

from app.auth.forms import ItalianForm
from app.calendar.palette import ACTIVITY_CATEGORIES

MAX_WEEKLY_REPEATS = 52


def _strip(value):
    return value.strip() if value else value


class ActivityForm(ItalianForm):
    category = SelectField(
        "Categoria",
        choices=[(key, data["label"]) for key, data in ACTIVITY_CATEGORIES.items()],
        validators=[DataRequired()],
    )
    title = StringField(
        "Titolo", filters=[_strip], validators=[DataRequired(), Length(max=200)]
    )
    starts_at = DateTimeLocalField("Inizio", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    ends_at = DateTimeLocalField("Fine", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    location = StringField("Luogo", filters=[_strip], validators=[Optional(), Length(max=200)])
    latitude = FloatField(
        "Latitudine", validators=[Optional(), NumberRange(min=-90, max=90)]
    )
    longitude = FloatField(
        "Longitudine", validators=[Optional(), NumberRange(min=-180, max=180)]
    )
    description = TextAreaField("Descrizione", filters=[_strip], validators=[Optional()])
    inscription_delay_date = DateField(
        "Scadenza iscrizione", validators=[Optional()]
    )
    weekly_repeats = IntegerField(
        "Ripeti ogni settimana per",
        default=1,
        validators=[Optional(), NumberRange(min=1, max=MAX_WEEKLY_REPEATS)],
    )
    submit = SubmitField("Salva attività")

    def __init__(self, *args, allow_repeat=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_repeat = allow_repeat

    @property
    def is_training(self):
        category = ACTIVITY_CATEGORIES.get(self.category.data)
        return bool(category) and category["activity_type"] == "allenamento"

    def validate_ends_at(self, field):
        if self.starts_at.data and field.data and field.data < self.starts_at.data:
            raise ValidationError("La fine non può precedere l'inizio.")

    def validate_longitude(self, field):
        if (self.latitude.data is None) != (field.data is None):
            raise ValidationError("Inserisci sia latitudine che longitudine, oppure nessuna delle due.")

    def validate_inscription_delay_date(self, field):
        if field.data is None:
            return
        if self.is_training:
            raise ValidationError("Gli allenamenti non hanno una scadenza di iscrizione.")
        if self.starts_at.data and field.data > self.starts_at.data.date():
            raise ValidationError("La scadenza non può essere dopo l'inizio dell'attività.")

    def validate_weekly_repeats(self, field):
        if field.data and field.data > 1 and not (self.allow_repeat and self.is_training):
            raise ValidationError("La ripetizione settimanale è disponibile solo per gli allenamenti.")
