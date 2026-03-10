"""
SkillQuest - Flask-WTF forms with validation.
"""
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from wtforms import ValidationError


def optional_date(form, field):
    """If provided, value must be YYYY-MM-DD."""
    if not field.data or not field.data.strip():
        return
    try:
        datetime.strptime(field.data.strip(), "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Deadline must be in YYYY-MM-DD format.")


class RegistrationForm(FlaskForm):
    """User registration: full name, email, password, role."""
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    role_id = SelectField("Role", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """Login: email and password."""
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class ChallengeForm(FlaskForm):
    """Create/edit challenge: title, description, category, difficulty, deadline."""
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired(), Length(max=80)])
    difficulty = SelectField(
        "Difficulty",
        choices=[("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")],
        validators=[DataRequired()],
    )
    deadline = StringField("Deadline (optional, YYYY-MM-DD)", validators=[Optional(), optional_date])
    submit = SubmitField("Save Challenge")


class SubmissionForm(FlaskForm):
    """Submit challenge: text answer required; optional file name placeholder."""
    text_answer = TextAreaField("Your Answer", validators=[DataRequired(), Length(min=1)])
    file_name = StringField("File name (optional)", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Submit")


class ReviewSubmissionForm(FlaskForm):
    """Admin review: score, status, feedback."""
    score = FloatField("Score (0–100)", validators=[Optional(), NumberRange(min=0, max=100)])
    status = SelectField(
        "Status",
        choices=[
            ("Pending", "Pending"),
            ("Reviewed", "Reviewed"),
            ("Late", "Late"),
            ("Rejected", "Rejected"),
        ],
        validators=[DataRequired()],
    )
    feedback = TextAreaField("Feedback (optional)", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save Review")
