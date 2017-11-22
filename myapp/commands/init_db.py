import datetime

from flask import current_app
from flask_script import Command

from myapp import db
#from app.models.user_models import User, Role
from myapp.models import User


class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()

def init_db():
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    #create_users()


def create_users():
    """ Create users """

    # Create all tables
    db.create_all()

    # Adding roles
    #admin_role = find_or_create_role('admin', u'Admin')

    # Add users
    #user = find_or_create_user(u'Admin', u'Example', u'admin@example.com', 'Password1', admin_role)
    user = find_or_create_user(u'araikc', u'alalo', u'araikc@gmail.com')

    # Save to DB
    db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(uname, password, email):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(username=uname,
                    password=password,
                    email=email)
        db.session.add(user)
    return user

