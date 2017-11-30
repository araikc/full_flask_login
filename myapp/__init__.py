
from flask import Flask, g
from flask_admin import Admin
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from werkzeug.contrib.fixers import ProxyFix
from .views.home import home
from .views.profile import userprofile
from .views.admin import MyAdminIndexView, AdminModelView

app = Flask(__name__)
admin = Admin(app, index_view=MyAdminIndexView(), base_template='admin/my_master.html', template_mode='bootstrap3')

from .lib import filters

# config
app.config.from_object('config.DevelopConfig')

# CSRFProtect
csrf = CSRFProtect(app)

# DB manager
db = SQLAlchemy(app)

from models import User
admin.add_view(AdminModelView(User, db.session))

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
    g.user = current_user

@app.context_processor
def inject_finance():
	from models import AccountInvestments
	if current_user.is_authenticated:
		investments = AccountInvestments.query.filter_by(accountId=current_user.accountId).all()
		inv = 0
		ern = 0
		for i in investments:
			inv += i.initialInvestment
			ern += i.initialInvestment - i.currentBalance
		return dict(g_investment=inv, g_earning=ern)
	return dict()

# register views
app.register_blueprint(home)
app.register_blueprint(userprofile)

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
  app.run()
