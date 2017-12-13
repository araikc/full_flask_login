from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..lib.decorators import check_confirmed
from ..forms import DepositForm, csrf
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
	ps = PaymentSystems.query.all()
	investmentPlans = InvestmentPlan.query.all()
	return render_template('profile/makedeposit.html', 
							invPlans=investmentPlans,
							paymentSystems=ps)


@userprofile.route('/confirm_deposit', methods=['POST'])
@login_required
@check_confirmed
def confirm_deposit():
	if request.method == 'POST':
		form = request.form
		psid = form.get('paymentSystemId', None)
		amount = form.get('amount', None)
		ipid = form.get('invPlanId', None)

		if psid and amount and ipid:
			from .. import db
			from ..models import InvestmentPlan
			from ..models import PaymentSystems
			from ..models import Transaction
			from ..models import TransactionType

			trType = TransactionType.query.filter_by(id=3).first()
			ps = PaymentSystems.query.filter_by(id=psid).first()
			ip = InvestmentPlan.query.filter_by(id=ipid).first()

			dep_act = Transaction(
									date=datetime.now(),
									amount=amount,
									status=0)
			dep_act.account = current_user.account
			dep_act.transactionType = trType
			dep_act.paymentSystem = ps
			dep_act.investmentPlan = ip
			db.session.add(dep_act)
			db.session.commit()


			return render_template('profile/confirm_deposit.html',
									invPlan=ip,
									paymentSystem=ps,
									amount=amount,
									depId=dep_act.id)
		else:
			flash('Invalid data supplied in deposit form')
			return redirect(url_for('userprofile.makedeposit'))

	else:
		return redirect(url_for('userprofile.makedeposit'))

@userprofile.route('/validate_deposit', methods=['POST'])
@login_required
@check_confirmed
def validate_deposit():
	if request.method == 'POST':
		from .. import app
		import hashlib

		pmsecret = app.config['PMSECRET'].upper()
		pmsecrethash = hashlib.md5(pmsecret).digest()
		form = request.form

		pid = form.get('PAYMENT_ID', None)
		pyacc = form.get('PAYEE_ACCOUNT', None)
		pam = form.get('PAYMENT_AMOUNT', None)
		pu = form.get('PAYMENT_UNITS', None)
		pbn = form.get('PAYMENT_BATCH_NUM', None)
		pracc = form.get('PAYER_ACCOUNT', None)
		ts = form.get('TIMESTAMPGMT', None)
		v2 = form.get('V2_HASH', None)

		if pid and pyacc and pam and pu and pbn and pracc and ts and v2:
			ver = "{0}:{1}:{2}:{3}:{4}:{5}:{6}:{7}".format(pid, pyacc, pam, pu, pbn, pracc, pmsecrethash, ts)
			verhash = hashlib.md5(ver).digest()

			if v2 != verhash:
				flash('Unable to complete deposit. Please try again.')
				return redirect(url_for('userprofile.makedeposit'))

			from .. import db
			from ..models import Transaction
			from ..models import AccountInvestments

			trans = Transaction.query.find_by(id=pid).first()
			trans.status = 1
			db.session.add(trans)

			# add investment
			accInv = AccountInvestments(
										currentBalance=pam,
										initialInvestment=pam,
										isActive=1)
			accInv.account = current_user.account
			accInv.paymentSystem = trans.paymentSystem
			accInv.investmentPlan = trans.investmentPlan
			accInv.startDatetime = datetime.now()
			accInv.endDatetime = accInv.startDatetime + datetime.timedelta(trans.investmentPlan.period) 
			accInv.pm_batch_num = pbn
			accInv.payment_unit = pu
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

			db.session.commit()

			flash('You are successfully invested', 'subccess')
			return redirect(url_for('userprofile.deposits'))			

		else:
			flash('Unable to complete deposit. Please try again.')
			return redirect(url_for('userprofile.makedeposit'))

	else:
		return redirect(url_for('userprofile.makedeposit'))

@userprofile.route('/deposit_success')
@login_required
@check_confirmed
def deposit_success():
	from .. import db
	from ..models import InvestmentPlan
	from ..models import PaymentSystems
	ps = PaymentSystems.query.all()
	investmentPlans = InvestmentPlan.query.all()
	return render_template('profile/makedeposit.html', 
							invPlans=investmentPlans,
							paymentSystems=ps)

@userprofile.route('/deposit_fail', methods=['POST', 'GET'])
@login_required
@check_confirmed
@csrf.exempt
def deposit_fail():
	from .. import csrf
	if request.method == 'GET':
		return render_template('profile/profile.html')
	else:
		return render_template('profile/profile.html')

@userprofile.route('/deposit_confirmation', methods=['POST'])
@login_required
@check_confirmed
def deposit_confirmation():
	from ..models import InvestmentPlan
	from ..models import PaymentSystems
	from ..models import AccountInvestments
	

	form = DepositForm(request.form)
	if form.validate():
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
							paymentSystems=ps)

@userprofile.route('/deposits')
@login_required
@check_confirmed
def deposits():
	from .. import db
	from ..models import AccountInvestments
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
	from ..forms import WalletsForm

	sql_cmd = '''select wallet.id, wallet.name, account_wallets.walletValue as value
	from wallet left join account_wallets 
	on wallet.id = account_wallets.walletId and account_wallets.accountId = {0} '''.format(current_user.account.id)
	wallets = db.engine.execute(sql_cmd).fetchall()

	wlist = []
	for w in wallets:
		wlist.append({'id' : w[0], 'name': w[1], 'value': w[2]})

	if request.method == 'POST':
		form = WalletsForm(request.form)
		if form.validate():
			pm = form.pmwallet.data.strip()
			bc = form.bcwallet.data.strip()
			for w in wlist:
				if w['id'] == 1:
					www = pm
				elif w['id'] == 2:
					www = bc

				wallet = Wallet.query.filter_by(id=w['id']).first()
				existAccWallet = AccountWallets.query.filter_by(accountId=current_user.account.id, walletId=wallet.id).first()
				if not existAccWallet:
						accWallet = AccountWallets(www)
						accWallet.account = current_user.account
						accWallet.wallet = wallet
						db.session.add(accWallet)
				else:
					existAccWallet.walletValue = www
				w['value'] = www
			db.session.commit()
			return render_template('profile/wallets.html', 
									wallets=wlist)
		else:
			return render_template('profile/wallets.html', 
								wallets=wlist)
	else:
		return render_template('profile/wallets.html', 
								wallets=wlist)







