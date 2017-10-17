
from flask import Flask, session, request, flash, url_for, redirect, render_template, abort, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm
from token2 import generate_confirmation_token, confirm_token
from flask_mail import Mail
from datetime import datetime
from decorators import check_confirmed

app = Flask(__name__)

# config
app.config.from_object('config.DevelopConfig')

# DB manager
db = SQLAlchemy(app)

# Email
mail = Mail()
mail.init_app(app)

# user login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# debuging
dtb = DebugToolbarExtension(app)

@login_manager.user_loader
def load_user(user_id):
	from models import User
	return User.query.get(user_id)

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register' , methods=['GET','POST'])
def register():
	from email2 import send_email
	from models import User
	if request.method == 'GET':
	    return render_template('register.html')
	form = RegistrationForm()
	if form.email.data:
		cur = User.query.filter_by(email=form.email.data).first()
		if cur is None:
			user = User(form.username.data, form.password.data, form.email.data)
			db.session.add(user)
			db.session.commit()
			token = generate_confirmation_token(user.email, app.config)
			confirm_url = url_for('confirm_email', token=token, _external=True)
			html = render_template('activate.html', confirm_url=confirm_url)
			subject = "Please confirm your email"
			send_email(user.email, subject, html, app.config)

			login_user(user)
			flash('A confirmation email has been sent via email.', 'success')
			return redirect(url_for('unconfirmed'))
		else:
			flash('User with specified email already exists in a system', 'warning')
	return render_template('register.html')
 
@app.route('/login',methods=['GET','POST'])
def login():
	from models import User
	if request.method == 'GET':
	    return render_template('login.html')

	email = request.form['email']
	password = request.form['password']
	remember_me = False
	if 'remember_me' in request.form:
	    remember_me = True
	user = User.query.filter_by(email=email).first()
	if user is None or not user.check_password(password):
	    flash('Username or Password is invalid' , 'error')
	    return redirect(url_for('login'))
	print user.is_authenticated
	login_user(user, remember = remember_me)
	print user.is_authenticated
	flash('Logged in successfully')
	return redirect(request.args.get('next') or url_for('index'))

@app.route('/confirm/<token>')
def confirm_email(token):
	from models import User
	email = None
	try:
	    email = confirm_token(token=token, config=app.config)
	except:
	    flash('The confirmation link is invalid or has expired.', 'danger')
	user = User.query.filter_by(email=email).first_or_404()
	if user.confirmed:
	    flash('Account already confirmed. Please login.', 'success')
	else:
	    user.confirmed = True
	    user.confirmed_on = datetime.now()
	    db.session.add(user)
	    db.session.commit()
	    flash('You have confirmed your account. Thanks!', 'success')
	return redirect(url_for('login'))

@app.route('/resend')
@login_required
def resend_confirmation():
	from email2 import send_email
	token = generate_confirmation_token(current_user.email, app.config)
	confirm_url = url_for('confirm_email', token=token, _external=True)
	html = render_template('activate.html', confirm_url=confirm_url)
	subject = "Please confirm your email"
	send_email(current_user.email, subject, html, app.config)
	flash('A new confirmation email has been sent.', 'success')
	return redirect(url_for('unconfirmed'))

@app.route('/unconfirmed')
@login_required
def unconfirmed():
	if current_user.confirmed:
	    return redirect('index')
	return render_template('unconfirmed.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')) 

@app.route('/profile')
@login_required
@check_confirmed
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
  app.run()
