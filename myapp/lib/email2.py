# project/email.py

from flask_mail import Message

from myapp import mail


def send_email(to, subject, template, config):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
