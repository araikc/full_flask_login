from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..lib.decorators import check_confirmed
from ..forms import DepositForm
from datetime import datetime

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
	from ..models import PaymentSystems
	#investments = AccountInvestments.query.filter_by(accountId=current_user.account.id).limit(5)
	investments = current_user.account.investments
	return render_template('profile/dashboard.html', 
							accId=current_user.account.id,
							accInvestments=investments)

@userprofile.route('/makedeposit')
@login_required
@check_confirmed
def makedeposit():
	from .. import db
	from ..models import InvestmentPlan
	from ..models import PaymentSystems
	accWallets = current_user.account.wallets.all()
	ps = PaymentSystems.query.all()
	investmentPlans = InvestmentPlan.query.all()
	return render_template('profile/makedeposit.html', 
							invPlans=investmentPlans,
							accWalletsLength=len(accWallets),
							paymentSystems=ps)


@userprofile.route('/deposit_confirmation', methods=['POST'])
@login_required
@check_confirmed
def deposit_confirmation():
	from ..models import InvestmentPlan
	from ..models import PaymentSystems
	from ..models import AccountInvestments
	

	form = DepositForm(request.form)
	if form.validate():
		if form.accWalletsLength.data == "0":
			flash('Please specify at least one wallet in "Payment info" section', 'warning')
			return render_template('profile/dashboard.html')
		else:
			from .. import db
			from ..models import Transaction
			from ..models import TransactionType
			from ..models import ReferralBonuses
			trType = TransactionType.query.filter_by(id=3).first()
			paymentSystemId = form.paymentSystemId.data
			ps = PaymentSystems.query.get(paymentSystemId)
			amount = form.amount.data
			invPlanId = form.invPlanId.data
			ip = InvestmentPlan.query.get(invPlanId)

			# add activity
			dep_act = Transaction(
									date=datetime.now(),
									amount=amount,
									status=0)
			dep_act.account = current_user.account
			dep_act.transactionType = trType
			db.session.add(dep_act)

			# add investment
			accInv = AccountInvestments(
										currentBalance=amount,
										initialInvestment=amount,
										idActive=1)
			accInv.account = current_user.account
			accInv.paymentSystem = ps
			accInv.investmentPlan = ip
			db.session.add(accInv)

			# add referral bonusess
			#refBon = ReferralBonuses(current_user.account.id, amount, )


			# add activity
			dep_act = Transaction(
									date=datetime.now(),
									amount=amount,
									status=1)

			dep_act.account = current_user.account
			dep_act.transactionType = trType
			db.session.add(dep_act)
			db.session.commit()

			flash('You are successfully invested', 'subccess')
			return redirect(url_for('userprofile.makedeposit'))
	else:
		flash('Please make sure all fields are specified', 'warning')
		accWallets = current_user.account.wallets
		ps = PaymentSystems.query.all()
		investmentPlans = InvestmentPlan.query.all()
		return render_template('profile/makedeposit.html', 
							invPlans=investmentPlans,
							accWalletsLength=len(accWallets),
							paymentSystems=ps)

@userprofile.route('/deposits')
@login_required
@check_confirmed
def deposits():
	from .. import db
	from ..models import AccountInvestments
	print current_user.account.investments
	investments = current_user.account.investments.order_by(AccountInvestments.endDatetime.desc()).limit(5)
	return render_template('profile/deposits.html', 
							accId=current_user.account.id,
							accInvestments=investments)

@userprofile.route('/activity')
@login_required
@check_confirmed
def activity():
	from .. import db
	from ..models import Transaction
	acts = current_user.account.transactions.order_by(Transaction.execDatetime.desc()).limit(5)
	return render_template('profile/activity.html', 
							accId=current_user.account.id,
							acts=acts)


@userprofile.route('/referrals')
@login_required
@check_confirmed
def referrals():
	from .. import db
	from ..models import Referral
	from ..models import AccountInvestments

	for rb in current_user.account.referralBonuses:
		print rb.invester_account_id

	referrals = []
	frefs = Referral.query.filter_by(accountId=current_user.account.id).all()
	srefs = []
	for fr in frefs:
		srefs.extend(Referral.query.filter_by(accountId=fr.refAccId).all())
	trefs = []
	for sr in srefs:
		trefs.extend(Referral.query.filter_by(accountId=sr.refAccId).all())
	#referrals.extend(frefs)
	#referrals.extend(srefs)

	data = []

	for ref in frefs:
		investments = ref.referralAccount.investments
		inv, ern = 0, 0
		for i in investments:
			inv += i.initialInvestment
		ern = inv / 100 * 5
		data.append({'username': ref.referralAccount.user.username, 
					 'investments': inv,
					 'earned': ern,
					 'level' : 1})

	return render_template('profile/referrals.html', 
							referrals=data)


