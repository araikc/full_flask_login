from flask import Flask, url_for, redirect, render_template, request, flash, g
import flask_admin as admin
from flask_login import logout_user, login_required
from flask_admin import helpers, expose
from flask_admin.contrib import sqla
from ..lib.decorators import required_roles
from wtforms import PasswordField
from flask_admin.actions import action

# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    @login_required
    @required_roles('admin')
    def index(self):
        return super(MyAdminIndexView, self).index()


    @expose('/logout/')
    @login_required
    @required_roles('admin')
    def logout_view(self):
        logout_user()
        return redirect(url_for('home.index'))

    def is_accessible(self):
       return g.user.is_authenticated and g.user.role == 'admin'


class UserModelView(sqla.ModelView):

    def is_accessible(self):
        return g.user.is_authenticated and g.user.role == 'admin'

    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password', 'account')

    list_template = 'admin/my_custom_action_list.html'

    column_display_pk = True

    form_choices = {
    'role': [
        ('admin', 'admin'),
        ('user', 'user'),
        ]
    }


    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserModelView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        from ..models import User

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = User.hash_password(model.password2)

class AccountModelView(sqla.ModelView):

    def is_accessible(self):
        return g.user.is_authenticated and g.user.role == 'admin'

    column_display_pk = True

    form_excluded_columns = ('transactions', 'investments', 'wallets', 'referralBonuses', 'withdraws', 'inherits', 'user')


class WithdrawModelView(sqla.ModelView):

    column_display_pk = True

    column_filters = ['status',]

    form_excluded_columns = ('status')

    @action('approve', 'Approve', 'Are you sure you want to approve withdraws to selected accounts?')
    def withdraw_accounts(self, ids):
        from ..models import Withdraws
        from ..models import Account
        from ..models import AccountWallets
        from ..models import Transaction
        from ..models import TransactionType
        from .. import db
        from .. import application
        from ..lib.email2 import send_email
        
        try:
            wths = Withdraws.query.filter(Withdraws.id.in_(ids), Withdraws.status==0).all()

            if len(wths) == 0:
                flash("Info: no pending withdraws found")
                return

            for w in wths:
                w.status = 1
                db.session.add(w)

                acc = Account.query.filter_by(id=w.accountId).first()
                accW = AccountWallets.query.filter_by(accountId=acc.id, walletId=w.walletId).first()

                if accW.wallet.unit == 'BTC':
                    acc.bitcoin -= w.amount
                else:
                    acc.balance -= w.amount
                db.session.add(acc)                    
                db.session.commit()

                html = render_template('home/withdraw_landed.html', account=acc, amount=w.amount, accW=accW)
                subject = "Withdraw received"
                send_email(acc.user.email, subject, html, application.config)

            flash("Success: mail was sent to users about withdrawals: %s" % (str(len(wths))))
        except Exception as ex:
            print "{}".format(str(ex))
            flash("Fail: please try again")


    def is_accessible(self):
        return g.user.is_authenticated and g.user.role == 'admin'

