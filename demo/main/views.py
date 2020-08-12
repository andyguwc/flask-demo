from flask import render_template, redirect, request, url_for

from . import main_bp
from demo.models import User
from demo.app import db

@main_bp.route('/')
def index():
    return render_template('main/index.html')


