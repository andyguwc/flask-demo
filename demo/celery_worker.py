#!/usr/bin/env python
import os
from demo.app import celery, create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
