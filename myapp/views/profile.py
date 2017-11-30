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
	from .. import db
	from ..models import AccountInvestments
	investments = AccountInvestments.query.filter_by(accountId=current_user.accountId).limit(5)
	return render_template('profile/dashboard.html', 
							accId=current_user.accountId,
							accInvestments=investments)