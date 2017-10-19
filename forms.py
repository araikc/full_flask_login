from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import Email, DataRequired, EqualTo

class LoginForm(Form):
    email = StringField('E-mail', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(LoginForm):
	password_repeat = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
	username = StringField('Username', validators=[DataRequired()])

class RequestResetPassordForm(Form):
    email = StringField('E-mail', validators=[Email(), DataRequired()])

class ResetPassordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])