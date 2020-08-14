# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from celery import Celery

from demo.config import config, Config

db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
celery = Celery(__name__, 
                backend=Config.CELERY_RESULT_BACKEND,
                broker=Config.CELERY_BROKER_URL)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'



def create_app(config_name):
    """Create Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    celery.conf.update(app.config)

    from demo import main, auth
    app.register_blueprint(main.main_bp)
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')

    return app