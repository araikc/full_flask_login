import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    TEMPLATES_AUTO_RELOAD = True
    SESSION_TIMEOUT = 30
    PMSECRET = ""
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
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_USERNAME = 'info@clickbuzzmedia.com'
    MAIL_PASSWORD = ''
    WTF_CSRF_SECRET_KEY = ''
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1/hpdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECURITY_PASSWORD_SALT = ""
    MAIL_DEFAULT_SENDER = "info@clickbuzzmedia.com"

