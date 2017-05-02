from flask import Flask
from config import config
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask_sslify import SSLify

mail = Mail()
moment = Moment()
db = SQLAlchemy(query_class=BaseQuery)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    
    # sslify = SSLify(app)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .api1 import api1 as api1_blueprint
    app.register_blueprint(api1_blueprint, url_prefix='/api1')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .mod import mod as mod_blueprint
    app.register_blueprint(mod_blueprint, url_prefix='/mod')
    
    from .personal import personal as personal_blueprint
    app.register_blueprint(personal_blueprint, url_prefix='/personal')
    
    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix='/u')

    return app