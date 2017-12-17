import datetime

from flask import current_app
from flask_script import Command

from myapp import db
from myapp.models import User
from myapp.models import Account
from myapp.models import ReferralProgram
from myapp.models import Wallet
from myapp.models import PaymentSystems
from myapp.models import InvestmentPlan
from myapp.models import AccountWallets
from myapp.models import TransactionType



class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()

def init_db():
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    create_admin_users()


def create_admin_users():
    """ Create users """

    refProg, wallet = craete_utils()

    account = create_account(refProg)

    # Add users
    user = create_user(account)

    aw = AccountWallets("url")
    aw.account = account
    aw.wallet = wallet
    db.session.add(aw)

    db.session.commit()


def create_account(rp):
    # Account User
    account = Account(0, 0)
    account.referralProgram = rp
    db.session.add(account)
    #db.session.commit()
    return account


def create_user(account):
    """ Find existing user or create new user """
    user = User(username=u'araikc', password=u'alalo', 
                               email=u'araikc@gmail.com', role='admin',
                               confirmed=1)
    user.account = account
    db.session.add(user)
    #db.session.commit()
    return user

def craete_utils():

    # refereal program
    rp = ReferralProgram("521", 5, 2, 1)
    db.session.add(rp)
    rp1 = ReferralProgram("731", 7, 3, 1)
    db.session.add(rp1)
    #db.session.commit()


    pm = PaymentSystems("Perfect money", "logo", "url")
    db.session.add(pm)
    bc = PaymentSystems("BitCoint", "logo", "url")
    db.session.add(bc)

    wallet = Wallet("Perfect Money", "url")
    wallet.paymentSystem = pm
    wallet.unit = 'USD'
    db.session.add(wallet)

    wallet = Wallet("Perfect Money", "url")
    wallet.paymentSystem = pm
    wallet.unit = 'EURO'
    db.session.add(wallet)

    ip = InvestmentPlan(8, 1, 8, "8% per day")
    ip1 = InvestmentPlan(14, 0, 115, "115% after 14 days")
    db.session.add(ip)
    db.session.add(ip1)
    #db.session.commit()

    tr = TransactionType("Login")
    db.session.add(tr)
    tr = TransactionType("Logout")
    db.session.add(tr)
    tr = TransactionType("Request deposit")
    db.session.add(tr)
    tr = TransactionType("Re-invest")
    db.session.add(tr)
    tr = TransactionType("Withdraw")
    db.session.add(tr)
    tr = TransactionType("Reset password")
    db.session.add(tr)
    tr = TransactionType("Change settings")
    db.session.add(tr)
    #db.session.commit()

    return rp, wallet

