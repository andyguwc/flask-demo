from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
login_manager = LoginManager()
migrate = Migrate()
celery = Celery()
