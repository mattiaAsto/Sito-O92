from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "gif"]
IMAGE_MESSAGE = "Sono ammesse solo immagini (jpg, png, webp, gif)."


class NewsForm(FlaskForm):
    title = StringField(
        "Titolo",
        filters=[lambda value: value.strip() if value else value],
        validators=[DataRequired(), Length(max=200)],
    )
    summary = StringField(
        "Sottotitolo",
        filters=[lambda value: value.strip() if value else value],
        validators=[Optional(), Length(max=200)],
    )
    text = TextAreaField("Testo (markdown)", validators=[DataRequired()])
    thumbnail = FileField(
        "Miniatura",
        validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, IMAGE_MESSAGE)],
    )
    submit = SubmitField("Pubblica")
