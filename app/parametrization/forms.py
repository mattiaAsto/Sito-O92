"""Admin forms for parametrization data."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, validators
from wtforms.validators import DataRequired, URL, Email, Optional


class ActivityForm(FlaskForm):
    """Form for editing activities."""
    tab = StringField('Tab Name', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    caption = StringField('Caption', validators=[DataRequired()])
    image = StringField('Image Filename', validators=[Optional()])
    
    class Meta:
        csrf = True


class DisciplineForm(FlaskForm):
    """Form for editing race disciplines."""
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    
    class Meta:
        csrf = True


class CommitteeMemberForm(FlaskForm):
    """Form for editing committee members."""
    role = StringField('Role', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional()])
    
    class Meta:
        csrf = True


class MonitorForm(FlaskForm):
    """Form for editing monitors."""
    name = StringField('Name', validators=[DataRequired()])
    
    class Meta:
        csrf = True


class ContactForm(FlaskForm):
    """Form for editing contacts."""
    role = StringField('Role', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    
    class Meta:
        csrf = True


class LinkGroupForm(FlaskForm):
    """Form for editing link groups."""
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    
    class Meta:
        csrf = True


class LinkForm(FlaskForm):
    """Form for editing links."""
    label = StringField('Label', validators=[DataRequired()])
    href = StringField('URL', validators=[DataRequired(), URL()])
    
    class Meta:
        csrf = True


class ClubForm(FlaskForm):
    """Form for editing clubs."""
    label = StringField('Label', validators=[DataRequired()])
    href = StringField('URL', validators=[DataRequired(), URL()])
    logo = StringField('Logo Filename', validators=[Optional()])
    
    class Meta:
        csrf = True


class SponsorForm(FlaskForm):
    """Form for editing sponsors."""
    label = StringField('Label', validators=[DataRequired()])
    href = StringField('URL', validators=[DataRequired(), URL()])
    logo = StringField('Logo Filename', validators=[Optional()])
    
    class Meta:
        csrf = True


class SettingForm(FlaskForm):
    """Form for editing settings."""
    value = TextAreaField('Value', validators=[DataRequired()])
    
    class Meta:
        csrf = True


class ShopMaterialForm(FlaskForm):
    """Form for editing shop materials."""
    slug = StringField('Slug', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    note = TextAreaField('Note', validators=[Optional()])
    contact_name = StringField('Contact Name', validators=[Optional()])
    contact_email = StringField('Contact Email', validators=[Optional(), Email()])
    
    class Meta:
        csrf = True


class CalendarCategoryForm(FlaskForm):
    """Form for editing calendar categories."""
    key = StringField('Key', validators=[DataRequired()])
    activity_type = SelectField(
        'Activity Type',
        choices=[('allenamento', 'Allenamento'), ('gara', 'Gara'), ('attivita', 'Attività')],
        validators=[DataRequired()]
    )
    label = StringField('Label', validators=[DataRequired()])
    color = StringField('Color (hex)', validators=[DataRequired()])
    
    class Meta:
        csrf = True
