from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
    DateTimeField,
    SelectField,
    PasswordField
)
from wtforms.validators import DataRequired, Length, Email
from models import default_due_date


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    due_date = DateTimeField("Due date",
                             default=default_due_date,
                             format="%Y-%m-%d %H:%M:%S"
                             )
    status = StringField("Status", default="new")
    attachment = StringField("Attachment")
    user_id = SelectField("Select user", coerce=int,
                          validators=[DataRequired()])
    submit = SubmitField("Сreate a task")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(),
                                                   Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
