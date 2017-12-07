from functools import wraps

from flask import flash, redirect, url_for, g, render_template, request
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('home.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function

def required_roles(*roles):
   def wrapper(f):
      @wraps(f)
      def wrapped(*args, **kwargs):
         if get_current_user_role() not in roles:
            return render_template('404.html'), 404
         return f(*args, **kwargs)
      return wrapped
   return wrapper
 
def get_current_user_role():
   return g.user.role

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.is_authenticated:
            return redirect(request.host_url)
        return f(*args, **kwargs)
    return decorated_function