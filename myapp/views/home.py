from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm, RegistrationForm, RequestResetPassordForm, ResetPassordForm
from datetime import datetime
from ..lib.token2 import generate_confirmation_token, confirm_token
from ..lib.decorators import check_confirmed

home = Blueprint('home', __name__)

@home.route('/')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('userprofile.dashboard'))
	else:
		return render_template('home/index.html')

@home.route('/register' , methods=['GET','POST'])
def register():
	from .. import app, db
	from ..lib.email2 import send_email
	from ..models import *
	if request.method == 'GET':
	    return render_template('home/register.html')
	form = RegistrationForm(request.form)
	if form.validate:
		cur = User.query.filter_by(email=form.email.data).first()
		if cur is None:
			# refereal program
			rp = ReferralProgram("521")
			db.session.add(rp)
			db.session.commit()

			# Account User
			account = Account(0, 0, rp.id)
			user = User(form.username.data, form.password.data, form.email.data)
			db.session.add(user)
			db.session.add(account)
			db.session.commit()

			token = generate_confirmation_token(user.email, app.config)
			confirm_url = url_for('home.confirm_email', token=token, _external=True)
			html = render_template('home/activate_email.html', confirm_url=confirm_url)
			subject = "Please confirm your email"
			send_email(user.email, subject, html, app.config)

			login_user(user)
			flash('A confirmation email has been sent via email.', 'success')
			return redirect(url_for('home.unconfirmed'))
		else:
			flash('User with specified email already exists in a system', 'warning')
	return render_template('home/register.html')
 
@home.route('/login',methods=['GET','POST'])
def login():
	from ..models import User
	if request.method == 'GET':
	    return render_template('home/login.html')
	form = LoginForm(request.form)
	if form.validate():
		email = form.email.data
		password = form.password.data
		remember_me = False
		if 'remember_me' in request.form:
		    remember_me = True
		user = User.query.filter_by(email=email).first()
		if user is None or not user.check_password(password):
		    flash('Username or Password is invalid' , 'error')
		    return redirect(url_for('home.login'))
		login_user(user, remember = remember_me)
		flash('Logged in successfully')
		return redirect(request.args.get('next') or url_for('userprofile.dashboard'))
	flash('Please check your inputs' , 'error')
	return redirect(url_for('home.login'))

@home.route('/view_reset_pass')
def view_reset_pass():
	return render_template('home/view_reset_pass.html')

@home.route('/confirm/<token>')
def confirm_email(token):
	from .. import app, db
	from ..models import User
	email = None
	try:
		email = confirm_token(token=token, config=app.config)
	except Exception as e:
	    flash('The confirmation link is invalid or has expired.', 'danger')
	    return redirect(url_for('home.register'))
	user = User.query.filter_by(email=email).first_or_404()
	if user.confirmed:
	    flash('Account already confirmed. Please login.', 'success')
	else:
	    user.confirmed = True
	    user.confirmed_on = datetime.now()
	    db.session.add(user)
	    db.session.commit()
	    flash('You have confirmed your account. Thanks!', 'success')
	return redirect(url_for('home.login'))

@home.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	email = None
	try:
	    email = confirm_token(token=token, config=app.config)
	except:
	    flash('The reset password link is invalid or has expired.', 'danger')
	    return redirect('login')
	return render_template('home/reset_password.html', email=email)

@home.route('/send_reset_pass', methods=['GET', 'POST'])
def send_reset_pass():
	from ..lib.email2 import send_email
	from ..models import User
	form = RequestResetPassordForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = generate_confirmation_token(form.email.data, app.config)
			reset_url = url_for('home.reset_password', token=token, _external=True)
			html = render_template('home/reset_password_email.html', reset_url=reset_url)
			subject = "Reset password request"
			send_email(form.email.data, subject, html, app.config)
			flash('We have sent you a link for resseting password.', 'success')
		else:
			flash('No user found with specified email.', 'warning')
			return redirect('view_reset_pass')
	return redirect('login')

@home.route('/save_reset_pass', methods=['POST'])
def save_reset_pass():
	from ..lib.email2 import send_email
	from ..models import User
	form = ResetPassordForm(request.form)
	if form.validate():
		user = User.query.filter_by(email=request.form['email']).first()
		if user:
			user.password = User.hash_password(form.password.data)
			db.session.add(user)
			db.session.commit()
			html = 'Thank you! You have successfully reset your password.'
			subject = "Reset password"
			send_email(request.form['email'], subject, html, app.config)
			flash('Thank you! You have successfully reset your password.')
		else:
			flash('No user found with specified email.', 'warning')
	return redirect('login')


@home.route('/resend')
@login_required
def resend_confirmation():
	from ..lib.email2 import send_email
	token = generate_confirmation_token(current_user.email, app.config)
	confirm_url = url_for('home.confirm_email', token=token, _external=True)
	html = render_template('home/activate_email.html', confirm_url=confirm_url)
	subject = "Please confirm your email"
	send_email(current_user.email, subject, html, app.config)
	flash('A new confirmation email has been sent.', 'success')
	return redirect(url_for('home.unconfirmed'))

@home.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.index')) 

@home.route('/unconfirmed')
@login_required
def unconfirmed():
	if current_user.confirmed:
	    return redirect('index')
	return render_template('home/unconfirmed.html')

