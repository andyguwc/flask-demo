# -*- coding: utf-8 -*-
import stripe

from flask import Flask

import demo.commands as commands

from demo.config import config
from demo.extensions import db, bootstrap, mail, login_manager, migrate, celery, moment
from demo.utils.celery import init_celery


def create_app(config_name='default'):
    """Create Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    register_extensions(app)

    from demo import main, auth, api, billing
    app.register_blueprint(main.main_bp)
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    app.register_blueprint(api.api_bp, url_prefix='/api/v1')
    app.register_blueprint(billing.billing_bp, url_prefix='/billing')
    init_celery(celery, app)

    register_commands(app)
    return app


def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    
    login_manager.login_view = 'auth.login'
    
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.api_version = app.config.get('STRIPE_API_VERSION')


def register_commands(app):
    app.cli.add_command(commands.deploy)
    app.cli.add_command(commands.clean)    
    app.cli.add_command(commands.comment_test)