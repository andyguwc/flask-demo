# -*- coding: utf-8 -*-
import os 


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my secret key')
    FLASK_APP = 'run.py'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configs
    MAIL_SERVER = os.getenv('MAIL_SERVER','smtp.googlemail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[TEST]'
    MAIL_SENDER_DEFAULT = 'FLASK DEVELOPMENT <flask@example.com>'
    DEMO_ADMIN = os.environ.get('DEMO_ADMIN')
    
    # OAuth credentials
    OAUTH_CREDENTIALS = {
        'github': {
            'client_id': os.environ.get('GITHUB_CLIENT_ID'),
            'client_secret': os.environ.get('GITHUB_CLIENT_SECRET')
        },
        'google': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET')
        }
    }
    OAUTHLIB_INSECURE_TRANSPORT='1'
    
    # Celery configs
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    
    # SQL configs
    POSTS_PER_PAGE = 20
    SLOW_DB_QUERY_TIME = 1
    
    # Stripe configs
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_API_VERSION = '2020-03-02'
    STRIPE_PLANS = {
        '0': {
            'id': 'bronze',
            'name': 'Bronze',
            'amount': 100,
            'currency': 'usd',
            'interval': 'month',
            'interval_count': 1,
            'trial_period_days': 14,
            'statement_descriptor': 'BRONZE',
            'metadata': {}
        },
        '1': {
            'id': 'gold',
            'name': 'Gold',
            'amount': 500,
            'currency': 'usd',
            'interval': 'month',
            'interval_count': 1,
            'trial_period_days': 14,
            'statement_descriptor': 'GOLD',
            'metadata': {
                'recommended': True
            }
        },
        '2': {
            'id': 'platinum',
            'name': 'Platinum',
            'amount': 1000,
            'currency': 'usd',
            'interval': 'month',
            'interval_count': 1,
            'trial_period_days': 14,
            'statement_descriptor': 'PLATINUM',
            'metadata': {}
        }
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    FLASK_ENV = 'production'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # log to stderr
        import logging
        from logging import StreamHandler
        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig, 
    'production': ProductionConfig,

    'default': DevelopmentConfig
}