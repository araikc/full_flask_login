import os

workers = int(os.environ.get('GUNICORN_PROCESSES', '3'))
threads = int(os.environ.get('GUNICORN_THREADS', '1'))

forwarded_allow_ips = '*'
secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    TEMPLATES_AUTO_RELOAD = True
    SESSION_TIMEOUT = 30
    PMSECRET = "SECRET"
    ADMIN_EMAIL = "araikc@gmail.com"

class ProductionConfig(Config):
    DEBUG = False
    MAIL_SERVER = "smtp.zoho.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''

class DevelopConfig(Config):
    DEBUG = False
    ASSETS_DEBUG = True
    MAIL_SERVER = "smtp.zoho.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'info@solarbit.biz'
    MAIL_PASSWORD = ''
    WTF_CSRF_SECRET_KEY = '12j1j1lk31k2312313'
    SECRET_KEY = '\x01\xc8$\x97\xd9\x1a\x13\xd9\x9eE\xabS\xc8\x17\xa4\xc3\x14\xe8Re\x94\x8cKR'
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECURITY_PASSWORD_SALT = "112233445566778899"
    MAIL_DEFAULT_SENDER = "info@solarbit.biz"

