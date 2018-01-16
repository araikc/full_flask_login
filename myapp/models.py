from . import db
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash


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

    ####
    account = db.relationship('Account', backref='user', uselist=False)

    def __init__(self, username, password, email, confirmed=None, confirmed_on=None, role='user'):
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

    def __unicode__(self):
        return self.username or ''

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0)
    bitcoin = db.Column(db.Float, nullable=True)
    
    referralProgramId = db.Column(db.Integer, db.ForeignKey('referral_programs.id'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    wallets = db.relationship('AccountWallets', backref='account', lazy='dynamic')
    inherits = db.relationship('Referral', backref='referralAccount', lazy='dynamic')
    investments = db.relationship('AccountInvestments', backref='account', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')
    referralBonuses = db.relationship('ReferralBonuses', backref='earnedAccount', lazy='dynamic')
    withdraws = db.relationship('Withdraws', backref='account', lazy='dynamic')

    def __init__(self, balance, bc):
        self.balance = balance
        self.bitcoin = bc

    def __unicode__(self):
        return str(self.id) or ''

class ReferralProgram(db.Model):
    __tablename__ = "referral_programs"

    # 1 - 5/2/1, 2 - 7/3/1 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    level1 = db.Column(db.Integer, nullable=True)
    level2 = db.Column(db.Integer, nullable=True)
    level3 = db.Column(db.Integer, nullable=True)

    accounts = db.relationship('Account', backref='referralProgram', lazy='dynamic')

    def __init__(self, name, l1=None, l2=None, l3=None):
        self.name = name
        self.level1 = l1
        self.level2 = l2
        self.level3 = l3

    def __unicode__(self):
        return self.name or ''

class TransactionType(db.Model):
    __tablename__ = "transaction_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), default="")

    transactions = db.relationship('Transaction', backref='transactionType', lazy='dynamic')

    def __init__(self, name):
        self.name = name

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    
    execDatetime = db.Column(db.DateTime, nullable=False)
    
    transactionTypeId = db.Column(db.Integer, db.ForeignKey('transaction_types.id'), nullable=False)
    investmentPlanId = db.Column(db.Integer, db.ForeignKey('investment_plans.id'), nullable=True)
    paymentSystemId = db.Column(db.Integer, db.ForeignKey('payment_systems.id'), nullable=True)

    amount = db.Column(db.Float, nullable=True)
    unit   = db.Column(db.String(5), nullable=True)
    status = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, date, amount, status):
        self.execDatetime = date
        self.amount = amount
        self.status = status

class Referral(db.Model):
    __tablename__ = "referrals"

    #id = db.Column(db.Integer, primary_key=True)
    accountId = db.Column(db.Integer, nullable=False, primary_key=True)
    refAccId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, primary_key=True)

    #level = db.Column(db.Integer, nullable=False)

    def __init__(self, accountId):
        self.accountId = accountId

class InvestmentPlan(db.Model):
    __tablename__ = "investment_plans"

    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, nullable=False)
    # 1 - hour, 2 - day, 3 - week, 4 - month
    periodUnit = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50), nullable=True)

    acountInvestments = db.relationship('AccountInvestments', backref='investmentPlan', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='investmentPlan', lazy='dynamic')

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

    acountInvestments = db.relationship('AccountInvestments', backref='paymentSystem', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='paymentSystem', lazy='dynamic')
    wallets = db.relationship('Wallet', backref='paymentSystem', lazy='dynamic')

    def __init__(self, name, logo, url):
        self.name = name
        self.logo = logo
        self.url = url

class AccountInvestments(db.Model):
    __tablename__ = "account_investments"

    id = db.Column(db.Integer, primary_key=True)
    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    
    investmentPlanId = db.Column(db.Integer, db.ForeignKey('investment_plans.id'), nullable=False)
    #investmentPlan = db.relationship(InvestmentPlan, backref='investment_plans')
    
    startDatetime = db.Column(db.DateTime, nullable=True)
    endDatetime = db.Column(db.DateTime, nullable=True)
    currentBalance = db.Column(db.Float, nullable=False)
    initialInvestment = db.Column(db.Float, nullable=False)
    isActive = db.Column(db.Boolean, nullable=True, default=False)
    paymentSystemId = db.Column(db.Integer, db.ForeignKey('payment_systems.id'), nullable=False)
    pm_batch_num = db.Column(db.Integer, nullable=False)
    payment_unit = db.Column(db.String(10), nullable=True)
    #paymentSystem = db.relationship(PaymentSystems, backref='payment_systems')

    def __init__(self, 
                currentBalance, 
                initialInvestment, isActive, startDatetime=None, endDatetime=None):
        self.startDatetime = startDatetime
        self.endDatetime = endDatetime
        self.currentBalance = currentBalance
        self.initialInvestment = initialInvestment
        self.isActive = isActive

class Wallet(db.Model):
    __tablename__ = "wallet"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=True)
    url = db.Column(db.String(70), nullable=True, default='')
    paymentSystemId = db.Column(db.Integer, db.ForeignKey('payment_systems.id'), nullable=False)
    unit = db.Column(db.String(5), nullable=False, default='USD')

    accounts =  db.relationship('AccountWallets', backref='wallet', lazy='dynamic')
    withdraws =  db.relationship('Withdraws', backref='wallet', lazy='dynamic')

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __unicode__(self):
        return self.name or ''

class AccountWallets(db.Model):
    __tablename__ = "account_wallets"

    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, primary_key=True)
    walletId = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False, primary_key=True)
    #wallet = db.relationship(Wallet, backref='wallet')
    walletValue = db.Column(db.String(100), nullable=True)

    def __init__(self, value):
        self.walletValue = value

class ReferralBonuses(db.Model):
    __tablename__ = "referral_bonuses"

    id = db.Column(db.Integer, primary_key=True)

    invester_account_id = db.Column(db.Integer, nullable=False)
    earned_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    invested_amount = db.Column(db.Float, nullable=False)
    earned_amount = db.Column(db.Float, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    payed = db.Column(db.Boolean, nullable=True, default=False)
    dateTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    def __init__(self, invAccId, amount, earned, level):
        self.invester_account_id = invAccId
        self.invested_amount = amount
        self.earned_amount = earned
        self.level = level


class Withdraws(db.Model):
    __tablename__ = "withdraws"

    id = db.Column(db.Integer, primary_key=True)

    dateTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    accountId = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    walletId = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False, index=True)
    status = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, dateTime, amount, walletId):
        self.dateTime=dateTime
        self.amount=amount
        self.walletId=walletId







