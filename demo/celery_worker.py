#!/usr/bin/env python
import os 
from demo.app import create_app
from demo.utils.celery import init_celery
from demo.extensions import celery

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
init_celery(celery, app)