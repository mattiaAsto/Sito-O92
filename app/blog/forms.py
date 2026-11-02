from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "gif"]
IMAGE_MESSAGE = "Sono ammesse solo immagini (jpg, png, webp, gif)."


def _strip(value):
    return value.strip() if value else value


class BlogPostForm(FlaskForm):
    title = StringField("Titolo", filters=[_strip], validators=[DataRequired(), Length(max=200)])
    summary = StringField("Sottotitolo", filters=[_strip], validators=[Optional(), Length(max=300)])
    text = TextAreaField("Testo (markdown)", validators=[DataRequired(), Length(max=100000)])
    cover = FileField(
        "Immagine di copertina",
        validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, IMAGE_MESSAGE)],
    )
    photos = MultipleFileField(
        "Foto del racconto",
        validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, IMAGE_MESSAGE)],
    )
    submit = SubmitField("Pubblica")
