from flask import Blueprint, flash, render_template , request
from flask_login import login_required, current_user
from ..lib.decorators import check_confirmed
from ..forms import DepositForm

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

@userprofile.route('/makedeposit')
@login_required
@check_confirmed
def makedeposit():
	from .. import db
	from ..models import InvestmentPlan
	from ..models import PaymentSystems
	from ..models import AccountWallets
	accWallets = AccountWallets.query.filter_by(accountId=current_user.accountId).all()
	ps = PaymentSystems.query.all()
	investmentPlans = InvestmentPlan.query.all()
	return render_template('profile/makedeposit.html', 
							invPlans=investmentPlans,
							accWalletsLength=len(accWallets),
							paymentSystems=ps)

@userprofile.route('/makedeposit', methods=['POST'])
@login_required
@check_confirmed
def depost_confirmation():
	form = DepositForm(request.form)
	if form.validate:
		if form.accWalletsLength.data == "0":
			flash('Please specify at least one wallet in "Payment info" section', 'warning')
			return render_template('profile/dashboard.html')
		else:
			from .. import db
			paymentSystemId = form.paymentSystemId.data
			amount = form.amount.data
			invPlanId = form.invPlanId.data
			from ..models import InvestmentPlan
			from ..models import PaymentSystems
			from ..models import AccountInvestments

			accInv = AccountInvestments(accountId=current_user.accountId, 
										investmentPlanId=invPlanId,
										currentBalance=amount,
										initialInvestment=amount,
										idActive=1,
										paymentSystemId=paymentSystemId)

			db.session.add(accInv)
			db.session.commit()

			invPlan = InvestmentPlan.query.filter_by(id=invPlanId).first()
			paymentSystem = PaymentSystems.query.filter_by(id=paymentSystemId).first()


			return render_template('profile/depositConfirmation.html', 
								invPlan=invPlan,
								amount=amount,
								paymentSystem=paymentSystem)
	else:
		flash('Please make sure all fields are specified', 'warning')
		return render_template('profile/makedeposit.html')





