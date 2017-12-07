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
			from ..models import Account
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
			firstLevelRefs = current_user.account.referrals
			for ref1 in firstLevelRefs:
				parentAcc = Account.query.filter_by(id=ref1.accountId).first()
				refProg = parentAcc.referralProgram
				perc = int(refProg.level1)
				refBon = ReferralBonuses(current_user.account.id, amount, float(float(amount) * perc  / 100), 1)
				refBon.earnedAccount = parentAcc
				db.session.add(refBon)
				secondLevelRefs = parentAcc.referrals
				for ref2 in secondLevelRefs:
					parentAcc = Account.query.filter_by(id=ref2.accountId).first()
					refProg = parentAcc.referralProgram
					perc = refProg.level2
					refBon = ReferralBonuses(current_user.account.id, amount, float(float(amount) * perc / 100), 2)
					refBon.earnedAccount = parentAcc
					db.session.add(refBon)
					thirdLevelRefs = parentAcc.referrals
					for ref3 in thirdLevelRefs:
						parentAcc = Account.query.filter_by(id=ref3.accountId).first()
						refProg = parentAcc.referralProgram
						perc = refProg.level3
						refBon = ReferralBonuses(current_user.account.id, amount, float(float(amount) * perc / 100), 3)
						refBon.earnedAccount = parentAcc
						db.session.add(refBon)

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
	from ..models import Account

	data = []
	for rb in current_user.account.referralBonuses:
		invAcc = Account.query.filter_by(id=rb.invester_account_id).first()
		data.append({'username' : invAcc.user.username,
					 'investment': rb.invested_amount,
					 'earned' : rb.earned_amount,
					 'level' : rb.level,
					 'status': rb.payed,
					 'date' : rb.dateTime})

	return render_template('profile/referrals.html', 
							referrals=data)

@userprofile.route('/wallets', methods=['GET', 'POST'])
@login_required
@check_confirmed
def wallets():
	from .. import db
	from ..models import Wallet
	from ..models import AccountWallets

	sql_cmd = '''select wallet.id, wallet.name, account_wallets.walletValue as value
	from wallet left join account_wallets 
	on wallet.id = account_wallets.walletId and account_wallets.accountId = {0} '''.format(current_user.account.id)
	wallets = db.engine.execute(sql_cmd).fetchall()

	return render_template('profile/wallets.html', 
							wallets=wallets)

