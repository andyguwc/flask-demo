# -*- coding: utf-8 -*-
import os 
from dotenv import load_dotenv
from flask_migrate import Migrate

from demo.app import create_app, db
from demo.models import User

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(dotenv_path)
    load_dotenv(dotenv_path)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)
