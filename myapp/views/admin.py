from flask import Flask, url_for, redirect, render_template, request, flash, g
import flask_admin as admin
from flask_login import logout_user, login_required
from flask_admin import helpers, expose
from flask_admin.contrib import sqla
from ..lib.decorators import required_roles
from wtforms import PasswordField


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


class AdminModelView(sqla.ModelView):

    def is_accessible(self):
        return g.user.is_authenticated and g.user.role == 'admin'

    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(AdminModelView, self).scaffold_form()

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
