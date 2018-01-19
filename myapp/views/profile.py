from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..lib.decorators import check_confirmed
from ..forms import DepositForm, csrf
import datetime

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
		unit = form.get('unit', None)

		if psid and amount and ipid and unit:
			from .. import db
			from ..models import InvestmentPlan
			from ..models import PaymentSystems
			from ..models import Transaction
			from ..models import TransactionType

			trType = TransactionType.query.filter_by(id=3).first()
			ps = PaymentSystems.query.filter_by(id=psid).first()
			ip = InvestmentPlan.query.filter_by(id=ipid).first()

			dep_act = Transaction(
									date=datetime.datetime.now(),
									amount=amount,
									status=0)
			dep_act.account = current_user.account
			dep_act.transactionType = trType
			dep_act.paymentSystem = ps
			dep_act.investmentPlan = ip
			dep_act.unit = unit
			db.session.add(dep_act)
			db.session.commit()


			return render_template('profile/confirm_deposit.html',
									invPlan=ip,
									paymentSystem=ps,
									amount=amount,
									depId=dep_act.id,
									unit=unit)
		else:
			flash('Invalid data supplied in deposit form')
			return redirect(url_for('userprofile.makedeposit'))

	else:
		return redirect(url_for('userprofile.makedeposit'))

@userprofile.route('/validate_deposit', methods=['POST'])
@login_required
@check_confirmed
@csrf.exempt
def validate_deposit():
	if request.method == 'POST':
		from .. import application
		import hashlib

		pmsecrethash = hashlib.md5(application.config['PMSECRET']).hexdigest().upper()
		form = request.form

		req_ip = request.remote_addr

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
			verhash = hashlib.md5(ver).hexdigest().upper()

			if v2 == verhash:
				from .. import db
				from ..models import Transaction
				from ..models import AccountInvestments
				from ..models import Referral
				from ..models import ReferralBonuses

				trans = Transaction.query.filter_by(id=pid).first()
				if trans.status == 0:
					trans.status = 1
					db.session.add(trans)
					ps = trans.paymentSystem
					ip = trans.investmentPlan

					# add investment
					accInv = AccountInvestments(
												currentBalance=pam,
												initialInvestment=pam,
												isActive=1)
					accInv.account = current_user.account
					accInv.paymentSystem = ps
					accInv.investmentPlan = ip
					accInv.startDatetime = datetime.datetime.now()
					accInv.endDatetime = accInv.startDatetime + datetime.timedelta(trans.investmentPlan.period) 
					accInv.pm_batch_num = pbn
					accInv.payment_unit = pu
					db.session.add(accInv)

					# parent account
					myRef = Referral.query.filter_by(accountId=current_user.account.id).first()
					if myRef:
						parentAcc = myRef.referralAccount
						refProg = parentAcc.referralProgram
						perc = int(refProg.level1)
						refBon = ReferralBonuses(current_user.account.id, pam, float(float(pam) * perc  / 100), 1)
						refBon.earnedAccount = parentAcc
						db.session.add(refBon)

						# grand parent account
						parentRef = Referral.query.filter_by(accountId=parentAcc.id).first()
						if parentRef:
							parentAcc = parentRef.referralAccount
							refProg = parentAcc.referralProgram
							perc = int(refProg.level2)
							refBon = ReferralBonuses(current_user.account.id, pam, float(float(pam) * perc  / 100), 2)
							refBon.earnedAccount = parentAcc
							db.session.add(refBon)

							# grand grand parent account
							grandRef = Referral.query.filter_by(accountId=parentAcc.id).first()
							if grandRef:
								parentAcc = grandRef.referralAccount
								refProg = parentAcc.referralProgram
								perc = int(refProg.level3)
								refBon = ReferralBonuses(current_user.account.id, pam, float(float(pam) * perc  / 100), 3)
								refBon.earnedAccount = parentAcc
								db.session.add(refBon)

					db.session.commit()
					####

					#send email to user
					from ..lib.email2 import send_email
					html = render_template('home/deposit_success_email.html', pam=pam, pu=pu, pyacc=pyacc, pbn=pbn, pracc=pracc)
					subject = "Congradulations! You have successfully deposited."
					send_email(current_user.email, subject, html, application.config)


@userprofile.route('/success_deposit', methods=['POST'])
@login_required
@check_confirmed
@csrf.exempt
def success_deposit():
	if request.method == 'POST':
		form = request.form
		pyacc = form.get('PAYEE_ACCOUNT', None)
		pam = form.get('PAYMENT_AMOUNT', None)
		pu = form.get('PAYMENT_UNITS', None)
		pbn = form.get('PAYMENT_BATCH_NUM', None)
		pracc = form.get('PAYER_ACCOUNT', None)
		pid = form.get('PAYMENT_ID', None)
		ts = form.get('TIMESTAMPGMT', None)
		v2 = form.get('V2_HASH', None)

		if pyacc and pam and pu and pbn and pracc and pid and ts and v2:
			
			#TEMP
			from .. import application
			import hashlib

			pmsecrethash = hashlib.md5(application.config['PMSECRET']).hexdigest().upper()
			ver = "{0}:{1}:{2}:{3}:{4}:{5}:{6}:{7}".format(pid, pyacc, str(pam), pu, pbn, pracc, pmsecrethash, ts)
			verhash = hashlib.md5(ver).hexdigest().upper()

			if v2 == verhash:
				from .. import db
				from ..models import Transaction
				from ..models import AccountInvestments
				from ..models import Referral
				from ..models import ReferralBonuses

				trans = Transaction.query.filter_by(id=pid).first()
				if trans.status == 0:
					trans.status = 1
					db.session.add(trans)
					ps = trans.paymentSystem
					ip = trans.investmentPlan

					# add investment
					accInv = AccountInvestments(
												currentBalance=pam,
												initialInvestment=pam,
												isActive=1)
					accInv.account = current_user.account
					accInv.paymentSystem = ps
					accInv.investmentPlan = ip
					accInv.startDatetime = datetime.datetime.now()
					accInv.endDatetime = accInv.startDatetime + datetime.timedelta(trans.investmentPlan.period) 
					accInv.pm_batch_num = pbn
					accInv.payment_unit = pu
					db.session.add(accInv)

					# parent account
					myRef = Referral.query.filter_by(accountId=current_user.account.id).first()
					if myRef:
						parentAcc = myRef.referralAccount
						refProg = parentAcc.referralProgram
						perc = int(refProg.level1)
						refBon = ReferralBonuses(current_user.account.id, pam, float(float(pam) * perc  / 100), 1)
						refBon.earnedAccount = parentAcc
						refBon.payed = True
						db.session.add(refBon)

						# update balance of parrent account
						# PM or BC
						if ps.id == 1:
							parentAcc.balance += float(float(pam) * perc  / 100)
						elif ps.id == 2:
							parentAcc.bitcoin += float(float(pam) * perc  / 100)
						db.session.add(parentAcc)

						# grand parent account
						parentRef = Referral.query.filter_by(accountId=parentAcc.id).first()
						if parentRef:
							parentAcc = parentRef.referralAccount
							refProg = parentAcc.referralProgram
							perc = int(refProg.level2)
							refBon = ReferralBonuses(current_user.account.id, pam, float(float(pam) * perc  / 100), 1)
							refBon.earnedAccount = parentAcc
							refBon.payed = True
							db.session.add(refBon)

							# update balance of parrent account
							if ps.id == 1:
								parentAcc.balance += float(float(pam) * perc  / 100)
							elif ps.id == 2:
								parentAcc.bitcoin += float(float(pam) * perc  / 100)
							db.session.add(parentAcc)

							# grand grand parent account
							grandRef = Referral.query.filter_by(accountId=parentAcc.id).first()
							if grandRef:
								parentAcc = grandRef.referralAccount
								refProg = parentAcc.referralProgram
								perc = int(refProg.level3)
								refBon = ReferralBonuses(current_user.account.id, pam, float(float(pam) * perc  / 100), 1)
								refBon.earnedAccount = parentAcc
								refBon.payed = True
								db.session.add(refBon)

								# update balance of parrent account
								if ps.id == 1:
									parentAcc.balance += float(float(pam) * perc  / 100)
								elif ps.id == 2:
									parentAcc.bitcoin += float(float(pam) * perc  / 100)
								db.session.add(parentAcc)

					db.session.commit()
					####

					#send email to user
					from ..lib.email2 import send_email
					html = render_template('home/deposit_success_email.html', pam=pam, pu=pu, pyacc=pyacc, pbn=pbn, pracc=pracc)
					subject = "Congradulations! You have successfully deposited."
					send_email(current_user.email, subject, html, application.config)

				return render_template('profile/success_deposit.html', 
									pyacc=pyacc,
									pam=pam,
									pu=pu,
									pbn=pbn,
									pracc=pracc)
			else:
				flash('Something goes worng. Please try again.')
				return redirect(url_for('userprofile.dashboard'))
		else:
			flash('Something goes worng. Please try again.')
			return redirect(url_for('userprofile.dashboard'))
	else:
		flash('Something goes worng. Please try again.')
		return redirect(url_for('userprofile.dashboard'))

@userprofile.route('/fail_deposit', methods=['POST'])
@login_required
@check_confirmed
@csrf.exempt
def fail_deposit():
	if request.method == 'POST':
		form = request.form
		pyacc = form.get('PAYEE_ACCOUNT', None)
		pam = form.get('PAYMENT_AMOUNT', None)
		pu = form.get('PAYMENT_UNITS', None)
		pbn = form.get('PAYMENT_BATCH_NUM', None)
		pracc = form.get('PAYER_ACCOUNT', None)
		pid = form.get('PAYMENT_ID', None)

		if pyacc and pam and pu:
			return render_template('profile/fail_deposit.html',
									pyacc=pyacc,
									pam=pam,
									pu=pu)
		else:
			flash('Something goes worng. Please try again.')
			return redirect(url_for('userprofile.dashboard'))
	else:
		flash('Something goes worng. Please try again.')
		return redirect(url_for('userprofile.dashboard'))

@userprofile.route('/deposits')
@login_required
@check_confirmed
def deposits():
	from .. import db
	from ..models import AccountInvestments
	investments = current_user.account.investments.filter_by(isActive=True).order_by(AccountInvestments.endDatetime.desc()).limit(5)
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
	from ..models import ReferralBonuses

	data = []
	for rb in current_user.account.referralBonuses.order_by(ReferralBonuses.dateTime.desc()).limit(5):
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

	sql_cmd = '''select wallet.id, wallet.name, account_wallets.walletValue as value, wallet.unit, wallet.paymentSystemId as psid
	from wallet left join account_wallets 
	on wallet.id = account_wallets.walletId and account_wallets.accountId = {0} '''.format(current_user.account.id)
	wallets = db.engine.execute(sql_cmd).fetchall()

	wlist = []
	for w in wallets:
		wlist.append({'id' : w[0], 'name': w[1], 'value': w[2], 'unit': w[3], 'psid': w[4]})

	if request.method == 'POST':
		form = WalletsForm(request.form)
		if form.validate():
			pmusd = form.pmwalletUSD.data.strip()
			pmeuro = form.pmwalletEURO.data.strip()
			bc = form.bcwallet.data.strip()
			for w in wlist:
				if w['psid'] == 1 and w['unit'] == 'USD':
					www = pmusd
				elif w['psid'] == 1 and w['unit'] == 'EURO':
					www = pmeuro
				elif w['psid'] == 2:
					www = bc

				wallet = Wallet.query.filter_by(id=w['id']).first()
				existAccWallet = AccountWallets.query.filter_by(accountId=current_user.account.id, walletId=wallet.id).first()
				if not existAccWallet and www != '':
						accWallet = AccountWallets(www)
						accWallet.account = current_user.account
						accWallet.wallet = wallet
						db.session.add(accWallet)
				else:
					if www != '':
						existAccWallet.walletValue = www
					else:
						# remove wallet
						AccountWallets.query.filter_by(accountId=current_user.account.id, walletId=wallet.id).delete()


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

@userprofile.route('/withdraw', methods=['GET'])
@login_required
@check_confirmed
def withdraw():
	from .. import db
	from ..models import Wallet
	accWallets = current_user.account.wallets.all()

	accWallets = None if len(accWallets) == 0 else accWallets

	if request.method == 'GET':
		return render_template('profile/withdraw.html', 
								accWallets=accWallets)

@userprofile.route('/confirm_withdraw', methods=['POST'])
@login_required
@check_confirmed
def confirm_withdraw():
	from .. import db
	from .. import application

	accWallets = current_user.account.wallets.all()

	accWallets = None if len(accWallets) == 0 else accWallets

	from ..models import AccountWallets
	from ..forms import WithdrawForm
	from ..models import TransactionType
	from ..models import Transaction

	form = WithdrawForm(request.form)
	if form.validate():
		accWalletId = form.accWalletId.data.strip()
		amount = form.amount.data.strip()

		accW = AccountWallets.query.filter(AccountWallets.walletId==accWalletId, AccountWallets.accountId==current_user.account.id).first()

		balance = current_user.account.balance if accW.wallet.unit == 'USD' or  accW.wallet.unit == 'EURO' else current_user.account.bitcoin

		if float(amount) <= 0:
			flash('Please specify positive amount')
			return render_template('profile/withdraw.html', 
								accWallets=accWallets)
		elif float(current_user.account.balance) < float(amount):
			flash('Insufficient balance')
			return render_template('profile/withdraw.html', 
								accWallets=accWallets)
		else:
			trType = TransactionType.query.filter_by(id=5).first()
			dep_act = Transaction(
									date=datetime.datetime.now(),
									amount=amount,
									status=0)
			dep_act.account = current_user.account
			dep_act.transactionType = trType
			dep_act.unit = accW.wallet.unit
			db.session.add(dep_act)

			db.session.commit()

		return render_template('profile/confirm_withdraw.html', 
								amount=amount,
								accWallet=accW,
								withId=dep_act.id)

@userprofile.route('/make_withdraw', methods=['POST'])
@login_required
@check_confirmed
def make_withdraw():

	from .. import db
	from .. import application
	accWallets = current_user.account.wallets.all()

	accWallets = None if len(accWallets) == 0 else accWallets

	from ..models import AccountWallets
	from ..models import Withdraws
	from ..models import Transaction
	from ..models import TransactionType
	from ..forms import ConfirmWithdrawForm

	form = ConfirmWithdrawForm(request.form)
	if form.validate():
		accWalletId = form.accWalletId.data.strip()
		amount = form.amount.data.strip()
		withdrawId = form.withdrawId.data.strip()

		accW = AccountWallets.query.filter(AccountWallets.walletId==accWalletId, AccountWallets.accountId==current_user.account.id).first()

		balance = current_user.account.balance if accW.wallet.unit == 'USD' or  accW.wallet.unit == 'EURO' else current_user.account.bitcoin

		wd = Transaction.query.filter_by(id=withdrawId).first()

		if float(amount) <= 0:
			flash('Please specify positive amount')
			return render_template('profile/withdraw.html', 
								accWallets=accWallets)
		elif float(current_user.account.balance) < float(amount):
			flash('Insufficient balance')
			return render_template('profile/withdraw.html', 
								accWallets=accWallets)
		elif wd.accountId != current_user.account.id or float(wd.amount) != float(amount) \
			   or wd.unit != accW.wallet.unit or wd.status != False:
			   	flash('Something goes wrong. please try agian.')
				return render_template('profile/withdraw.html', 
								accWallets=accWallets)
		else:
			from ..lib.email2 import send_email
			html = render_template('home/withdraw_request_email.html', account=current_user.account, amount=amount, accW=accW)
			subject = "New withdraw request"
			send_email(application.config['ADMIN_EMAIL'], subject, html, application.config)

			wd = Withdraws(datetime.datetime.now(), amount, accWalletId)
			wd.account = current_user.account
			wd.status = False
			db.session.add(wd)

			db.session.commit()

			#withs = current_user.account.withdraws.all()
			#return render_template('profile/withdraws_history.html',
			#					withs=withs,
			#					sent=True)
			flash("You have successfully sent withdraw request. Our backoffice team will withdraw to you wallet during 12 hours.")
			return redirect(url_for('userprofile.withdraws_history'))
	else:
		flash('Please recheck your input data')
		return render_template('profile/withdraw.html', 
				accWallets=accWallets)



@userprofile.route('/withdraws_history', methods=['GET'])
@login_required
@check_confirmed
def withdraws_history():
	from ..models import Withdraws

	withs = current_user.account.withdraws.order_by(Withdraws.dateTime.desc()).limit(5)

	if request.method == 'GET':
		return render_template('profile/withdraws_history.html', 
								withs=withs,
								sent=False)

