from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField
from wtforms.validators import Email, DataRequired, EqualTo, ValidationError

class LoginForm(Form):
    email = StringField('E-mail', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(LoginForm):
    password_repeat = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    username = StringField('Username', validators=[DataRequired()])
    refemail = StringField('Referral e-mail', validators=[Email()])

class RequestResetPassordForm(Form):
    email = StringField('E-mail', validators=[Email(), DataRequired()])

class ResetPassordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])

class DepositForm(Form):
    paymentSystemId = StringField('paymentSystemId', validators=[DataRequired()])
    amount = StringField('amount', validators=[DataRequired()])
    invPlanId = StringField('invPlanId', validators=[DataRequired()])
    accWalletsLength = StringField('accWalletsLength', validators=[DataRequired()])
