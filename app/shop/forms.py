from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import BooleanField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "gif"]
IMAGE_MESSAGE = "Sono ammesse solo immagini (jpg, png, webp, gif)."
MAX_PHOTOS = 6

CATEGORIES = ["Maglie", "Giacche", "Pantaloni", "Scarpe", "Accessori", "Altro"]


def _strip(value):
    return value.strip() if value else value


class ProductForm(FlaskForm):
    name = StringField("Nome articolo", filters=[_strip], validators=[DataRequired(), Length(max=100)])
    category = SelectField("Categoria", choices=[(c, c) for c in CATEGORIES])
    size = StringField("Taglia", filters=[_strip], validators=[Optional(), Length(max=20)])
    price = DecimalField(
        "Prezzo (CHF)",
        places=2,
        validators=[DataRequired(), NumberRange(min=0, max=100000)],
    )
    description = TextAreaField(
        "Descrizione", filters=[_strip], validators=[DataRequired(), Length(max=2000)]
    )
    contact_phone = StringField(
        "Telefono (facoltativo)", filters=[_strip], validators=[Optional(), Length(max=30)]
    )
    photos = MultipleFileField(
        "Foto",
        validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, IMAGE_MESSAGE)],
    )
    is_official_clothing = BooleanField("Abbigliamento ufficiale del team")
    submit = SubmitField("Pubblica")
