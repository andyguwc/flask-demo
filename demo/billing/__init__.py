# -*- coding: utf-8 -*-
from flask import Blueprint

billing_bp = Blueprint('billing', __name__)

from . import views
