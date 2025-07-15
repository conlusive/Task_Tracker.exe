from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegistrationForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Repeat password', [DataRequired(), EqualTo('password')])
    telegram_id = StringField("Telegram ID", validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    title = StringField('Task name', validators=[DataRequired()])
    is_done = BooleanField('Done')
    deadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Save')