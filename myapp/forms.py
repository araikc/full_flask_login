from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField, TextField, FieldList, FormField
from wtforms.validators import Email, DataRequired, EqualTo, ValidationError
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

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

class WalletsForm(Form):
    pmwalletUSD = StringField('pmwalletUSD')
    pmwalletEURO = StringField('pmwalletEURO')
    bcwallet = StringField('bcwallet')


class WithdrawForm(Form):
    accWalletId = StringField('accWalletId', validators=[DataRequired()])
    amount = StringField('amount', validators=[DataRequired()])

class ConfirmWithdrawForm(Form):
    withdrawId = StringField('withdrawId', validators=[DataRequired()])
    accWalletId = StringField('accWalletId', validators=[DataRequired()])
    amount = StringField('amount', validators=[DataRequired()])