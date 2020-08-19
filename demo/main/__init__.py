# -*- coding: utf-8 -*-
from flask import Blueprint

main_bp = Blueprint('main', __name__)

from . import views, errors
from demo.models import Permission

@main_bp.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)