import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    ADMIN = os.environ.get("ADMIN")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_PORT = 465
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_BACKEND_URL = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ('app.tasks',)
    CELERYBEAT_SCHEDULE = {
        'updates': {
            'task': 'app.tasks.updates',
            'schedule' : datetime.timedelta(seconds=30),
            'args': ("Message",)
        },
    }


    @staticmethod
    def init_app(app):
        pass

# On Cloud9, with SQLITE
class DevelopmentConfig(Config):
    DEBUG = True
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = \
            'sqlite:///' + os.path.join(basedir, 'db/data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# On Cloud9, with Postgres
class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://ubuntu:123456789@localhost:5432/data'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# On Heroku, with Postgres
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'development': DevelopmentConfig,
    'deployment': DeploymentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}