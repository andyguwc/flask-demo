# -*- coding: utf-8 -*-
import os 
from demo.app import create_app, db
from demo.models import User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)
