from flask import render_template, redirect, request, url_for, flash, session, current_app
from flask_login import current_user, login_user, logout_user, login_required
from requests_oauthlib import OAuth2Session

from . import auth_bp
from .forms import RegistrationForm, LoginForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from demo.models import User
from demo.extensions import db
from demo.tasks.email import send_email
from demo.utils.oauth import provider_class_map


# filtering unconfirmed accounts 
@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.blueprint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # send confirmation email
        token = user.generate_confirmation_token()
        send_email(
            to=user.email,
            subject='Confirmation Your Account',
            template='auth/email/confirm',
            username=user.username,
            token=token
        )
        flash('Signed Up. Confirmation Email Sent')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login Successful')
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password') 
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():        
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    """Confirm user email as user clicks the link
    """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        current_user.confirmed = True
        db.session.commit()
        flash('You have confirmed your account')
    else:
        flash('The confirmation link is invalid or expired')
    return redirect(url_for('main.index'))


@auth_bp.route('confirm')
@login_required
def resend_confirmation():
    """Resend confirmation for user already logged in but not confirmed yet
    """
    token = current_user.generate_confirmation_token()
    send_email(
        to=current_user.email,
        subject='Confirmation Your Account',
        template='auth/email/confirm',
        user=current_user,
        token=token
    )
    flash('Confirmation Email Resent')
    return redirect(url_for('main.index'))


@auth_bp.route('unconfirmed')
def unconfirmed():
    """Send unconfirmed users here
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Update password
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Password updated')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """Send password reset emails
    """
    if not current_user.is_anonymous:
        return rediret(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
            flash('An email to reset password has been sent')
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       username=current_user.username, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth_bp.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))


# implement oauth2 below
# using github as an example
@auth_bp.route('/login/<provider>')
def oauth_login(provider):
    """OAuth authorize redirect to request the provider oauth endpoint
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    # initialize provider wrapper
    oauth = provider_class_map[provider]()
    return oauth.authorize()


@auth_bp.route('/login/callback/<provider>')
def oauth_callback(provider):
    """Callback route, saves token in session and extract user information
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = provider_class_map[provider]()
    email, username = oauth.callback()
    # if user with email already exists, then don't create new user 
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, username=username, confirmed=True)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=True)
    return redirect(url_for('main.index'))
