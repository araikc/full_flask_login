from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm, RegistrationForm, RequestResetPassordForm, ResetPassordForm
from datetime import datetime
from ..lib.token2 import generate_confirmation_token, confirm_token
from ..lib.decorators import check_confirmed, logout_required
from datetime import datetime

home = Blueprint('home', __name__)

@home.route('/')
def index():
	# if current_user.is_authenticated:
	# 	return redirect(url_for('userprofile.dashboard'))
	# else:
	ref = request.args.get('ref')
	if ref != None:
		session['referral'] = ref
	return render_template('home/index.html')

@home.route('/service')
def service():
		return render_template('home/service.html')

@home.route('/about')
def about():
		return render_template('home/about.html')


@home.route('/faq')
def faq():
		return render_template('home/faq.html')


@home.route('/contact')
def contact():
		return render_template('home/contact.html')

@home.route('/register' , methods=['GET','POST'])
@logout_required
def register():
	#if 'referral' in session:
	#	print session['referral']
	from .. import application, db
	from ..lib.email2 import send_email
	from ..models import User, ReferralProgram, Account
	if request.method == 'GET':
		referral = None
		if 'referral' in session:
			referral = session['referral']
		return render_template('home/register.html', referral=referral)
	form = RegistrationForm(request.form)
	if form.validate():
		cur = User.query.filter_by(email=form.email.data).first()
		refUser = None

		if cur is None:

			# refereal program 521
			rp = ReferralProgram.query.filter_by(id=1).first()

			# Account User
			account = Account(0, 0)
			account.referralProgram = rp
			db.session.add(account)
			#db.session.commit()

			user = User(username=form.username.data, password=form.password.data, email=form.email.data)
			user.account = account
			db.session.add(user)
			#db.session.commit()

			# referral account
			if form.refemail.data:
				refUser = User.query.filter_by(email=form.refemail.data).first()
				if refUser:
					referral = Referral(accountId=account.id)
					referral.referralAccount = refUser.account
					db.session.add(referral)

			db.session.commit()

			token = generate_confirmation_token(user.email, application.config)
			confirm_url = url_for('home.confirm_email', token=token, _external=True)
			html = render_template('home/activate_email.html', confirm_url=confirm_url)
			subject = "Please confirm your email"
			send_email(user.email, subject, html, application.config)

			login_user(user)
			flash('A confirmation email has been sent via email.', 'success')
			return redirect(url_for('home.unconfirmed'))
		else:
			flash('User with specified email already exists in a system', 'warning')
	return render_template('home/register.html')
 

@home.route('/login',methods=['GET','POST'])
@logout_required
def login():
	from .. import db
	from ..models import User
	from ..models import Transaction
	from ..models import TransactionType
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
		tr = TransactionType.query.filter_by(id=1).first()
		if user is None or not user.check_password(password):
			flash('Username or Password is invalid' , 'error')
			if user:
				login_act = Transaction(
								date=datetime.now(),
								amount=None,
								status=0)
				login_act.account = user.account
				login_act.transactionType = tr
				db.session.add(login_act)
				db.session.commit()
			return redirect(url_for('home.login'))
		login_user(user, remember = remember_me)
		flash('Logged in successfully')
		login_act = Transaction(
								date=datetime.now(),
								amount=None,
								status=1)
		login_act.account = current_user.account
		login_act.transactionType = tr
		db.session.add(login_act)
		db.session.commit()
		return redirect(request.args.get('next') or url_for('userprofile.dashboard'))
	flash('Please check your inputs' , 'error')
	return redirect(url_for('home.login'))

@home.route('/view_reset_pass')
def view_reset_pass():
	return render_template('home/view_reset_pass.html')

@home.route('/confirm/<token>')
def confirm_email(token):
	from .. import application, db
	from ..models import User
	email = None
	try:
		email = confirm_token(token=token, config=application.config)
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
	from .. import application
	email = None
	try:
	    email = confirm_token(token=token, config=application.config)
	except:
	    flash('The reset password link is invalid or has expired.', 'danger')
	    return redirect('login')
	return render_template('home/reset_password.html', email=email)

@home.route('/send_reset_pass', methods=['GET', 'POST'])
def send_reset_pass():
	from ..lib.email2 import send_email
	from ..models import User
	from .. import application
	form = RequestResetPassordForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = generate_confirmation_token(form.email.data, application.config)
			reset_url = url_for('home.reset_password', token=token, _external=True)
			html = render_template('home/reset_password_email.html', reset_url=reset_url)
			subject = "Reset password request"
			send_email(form.email.data, subject, html, application.config)
			flash('We have sent you a link for resseting password.', 'success')
		else:
			flash('No user found with specified email.', 'warning')
			return redirect('view_reset_pass')
	return redirect('login')

@home.route('/save_reset_pass', methods=['POST'])
def save_reset_pass():
	from ..lib.email2 import send_email
	from ..models import User
	from ..models import Transaction
	from ..models import TransactionType
	from .. import application, db
	form = ResetPassordForm(request.form)
	if form.validate():
		user = User.query.filter_by(email=request.form['email']).first()
		if user:
			user.password = User.hash_password(form.password.data)
			db.session.add(user)
			tr = Transaction(datetime.now(), None, 1)
			tr.transactionTypeId = TransactionType.query.filter_by(id=6).first().id
			db.session.add(tr)
			db.session.commit()
			html = 'Thank you! You have successfully reset your password.'
			subject = "Reset password"
			send_email(request.form['email'], subject, html, application.config)
			flash('Thank you! You have successfully reset your password.')
		else:
			flash('No user found with specified email.', 'warning')
	return redirect('login')


@home.route('/resend')
@login_required
def resend_confirmation():
	from .. import application
	from ..lib.email2 import send_email
	token = generate_confirmation_token(current_user.email, application.config)
	confirm_url = url_for('home.confirm_email', token=token, _external=True)
	html = render_template('home/activate_email.html', confirm_url=confirm_url)
	subject = "Please confirm your email"
	send_email(current_user.email, subject, html, application.config)
	flash('A new confirmation email has been sent.', 'success')
	return redirect(url_for('home.unconfirmed'))

@home.route('/logout')
@login_required
def logout():
	from .. import db
	from ..models import Transaction
	from ..models import TransactionType
	trType = TransactionType.query.filter_by(id=2).first()
	logout_act = Transaction(
							date=datetime.now(),
							amount=None,
							status=1)
	logout_act.account = current_user.account
	logout_act.transactionType = trType
	db.session.add(logout_act)
	db.session.commit()
	logout_user()
	return redirect(url_for('home.index')) 

@home.route('/unconfirmed')
@login_required
def unconfirmed():
	if current_user.confirmed:
	    return redirect('index')
	return render_template('home/unconfirmed.html')

