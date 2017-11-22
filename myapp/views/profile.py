from flask import Blueprint, render_template 
from flask_login import login_required, current_user
from ..lib.decorators import check_confirmed

userprofile = Blueprint('userprofile', __name__)

@userprofile.route('/profile')
@login_required
@check_confirmed
def profile():
    return render_template('profile/profile.html')

@userprofile.route('/dashboard')
@login_required
@check_confirmed
def dashboard():
	from ..models import UserAccount
	user_account = UserAccount.query.filter_by(userId=current_user.get_id()).first()
	return render_template('profile/dashboard.html', accId=user_account.get_accountId())