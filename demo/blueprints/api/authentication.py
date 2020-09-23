# -*- coding: utf-8 -*-
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth

from . import api_bp
from .errors import unauthorized, forbidden
from demo.models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """authentication verification with either login credentials or tokens
    """
    if email_or_token == '':
        return False
    if password == '':
        # verify token
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    # verify email
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api_bp.before_request
@auth.login_required
def before_request():
    """All API routes require user to be authenticated
    """
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api_bp.route('/tokens/', methods=['POST'])
def get_token():
    """Route to request new tokens
    """
    # makes sure client needs to log in before asking new tokens
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
