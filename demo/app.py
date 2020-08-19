# -*- coding: utf-8 -*-
from flask import Flask
from demo.config import config
from demo.extensions import db, bootstrap, mail, login_manager, migrate, celery, moment
from demo.utils.celery import init_celery


def create_app(config_name='default'):
    """Create Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    configure_extensions(app)

    from demo import main, auth
    app.register_blueprint(main.main_bp)
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')

    init_celery(celery, app)

    return app


def configure_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    
    login_manager.login_view = 'auth.login'
