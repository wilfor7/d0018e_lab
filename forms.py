from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField("Username", validators=[DataRequired()])     # username is an email address
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class LogoutForm(FlaskForm):
    submit = SubmitField("Logout")
