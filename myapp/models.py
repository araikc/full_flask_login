from . import db
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Integer, nullable=False, default=0)
    bitcoin = db.Column(db.Integer, nullable=True)
    referralProgramId = db.Column(db.Integer, db.ForeignKey('referral_programs.id'), nullable=False)

    def __init__(self, balance, bc, rpid):
        self.balance = balance
        self.bitcoin = bc
        self.referralProgramId = rpid

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255))
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')

    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    account = db.relationship(Account, backref='accounts')

    def __init__(self, username, password, email, confirmed=None, confirmed_on=None, role='user', accountId=None):
        self.accountId = accountId
        self.username = username
        self.email = email
        self.password = User.hash_password(password)
        self.registered_on = datetime.now()
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)



class ReferralProgram(db.Model):
    __tablename__ = "referral_programs"

    # 1 - 5/2/1, 2 - 7/3/1 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, name):
        self.name = name

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    execDatetime = db.Column(db.DateTime, nullable=False)
    transactionTypeId = db.Column(db.Integer, db.ForeignKey('transaction_types.id'), nullable=False)
    amount = db.Column(db.Float, nullable=True)

class TransactionType(db.Model):
    __tablename__ = "transaction_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), default="")

class Referral(db.Model):
    __tablename__ = "referrals"

    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    refUserId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)

class InvestmentPlan(db.Model):
    __tablename__ = "investment_plans"

    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, nullable=False)
    # 1 - hour, 2 - day, 3 - week, 4 - month
    periodUnit = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50), nullable=True)

    def __init__(self, per, peru, perc, desc):
        self.period = per
        self.periodUnit = peru
        self.percentage = perc
        self.description = desc
        
class PaymentSystems(db.Model):
    __tablename__ = "payment_systems"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    logo = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(100), nullable=True)

class AccountInvestments(db.Model):
    __tablename__ = "account_investments"

    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, primary_key=True)
    investmentPlanId = db.Column(db.Integer, db.ForeignKey('investment_plans.id'), nullable=False, primary_key=True)
    investmentPlan = db.relationship(InvestmentPlan, backref='investment_plans')
    startDatetime = db.Column(db.DateTime, nullable=True)
    endDatetime = db.Column(db.DateTime, nullable=True)
    currentBalance = db.Column(db.Integer, nullable=False)
    initialInvestment = db.Column(db.Integer, nullable=False)
    idActive = db.Column(db.Boolean, nullable=True, default=False)
    paymentSystemId = db.Column(db.Integer, db.ForeignKey('payment_systems.id'), nullable=False)
    paymentSystem = db.relationship(PaymentSystems, backref='payment_systems')

    def __init__(self, accountId, investmentPlanId, 
                currentBalance, 
                initialInvestment, idActive, paymentSystemId, startDatetime=None, endDatetime=None):
        self.accountId = accountId
        self.investmentPlanId =investmentPlanId
        self.startDatetime = startDatetime
        self.endDatetime = endDatetime
        self.currentBalance = currentBalance
        self.initialInvestment = initialInvestment
        self.idActive = idActive
        self.paymentSystemId = paymentSystemId



class Wallet(db.Model):
    __tablename__ = "wallet"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)

class AccountWallets(db.Model):
    __tablename__ = "account_wallets"

    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, primary_key=True)
    walletId = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False, primary_key=True)
    wallet = db.relationship(Wallet, backref='wallet')
    walletValue = db.Column(db.String(100), nullable=True)





