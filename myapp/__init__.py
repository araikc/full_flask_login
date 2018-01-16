
from flask import Flask, g, session
from flask_admin import Admin
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
# from flask_wtf.csrf import CSRFProtect
from forms import csrf
from werkzeug.contrib.fixers import ProxyFix
from .views.home import home
from .views.profile import userprofile
from .views.admin import MyAdminIndexView, UserModelView, AccountModelView, WithdrawModelView

import datetime

app = Flask(__name__)
admin = Admin(app, index_view=MyAdminIndexView(), base_template='admin/my_master.html', template_mode='bootstrap3')

from .lib import filters

# config
app.config.from_object('config.DevelopConfig')
app.config['PMSECRET'] = os.env['PMSECRET'] if app.config['PMSECRET'] == '' else app.config['PMSECRET']
app.config['MAIL_USERNAME'] = os.env['MAIL_USERNAME'] if app.config['MAIL_USERNAME'] == '' else app.config['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.env['MAIL_PASSWORD'] if app.config['MAIL_PASSWORD'] == '' else app.config['MAIL_PASSWORD']
app.config['SQLALCHEMY_DATABASE_URI'] = os.env['SQLALCHEMY_DATABASE_URI'] if app.config['SQLALCHEMY_DATABASE_URI'] == '' else app.config['SQLALCHEMY_DATABASE_URI']


# CSRFProtect
csrf.init_app(app)

# DB manager
db = SQLAlchemy(app)

from models import User
admin.add_view(UserModelView(User, db.session))
from models import Account
admin.add_view(AccountModelView(Account, db.session))
from models import Withdraws
admin.add_view(WithdrawModelView(Withdraws, db.session))

# Email
mail = Mail(app)

# user login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home.login'

# debuging
dtb = DebugToolbarExtension(app)

@login_manager.user_loader
def load_user(user_id):
	from models import User
	return User.query.get(user_id)

@app.before_request
def before_request():
	session.permanent = True
	app.permanent_session_lifetime = datetime.timedelta(minutes=app.config['SESSION_TIMEOUT'])
	session.modified = True
	g.user = current_user

@app.context_processor
def inject_finance():
	from models import AccountInvestments
	if current_user.is_authenticated:
		investments = AccountInvestments.query.filter_by(accountId=current_user.account.id).all()
		inv = 0
		ern = 0
		for i in investments:
			inv += i.initialInvestment
			ern += i.currentBalance - i.initialInvestment
		return dict(g_investment=inv, g_earning=ern)
	return dict()

# register views
app.register_blueprint(home)
app.register_blueprint(userprofile)

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
  app.run()
