import stripe

from . import billing_bp
from flask import render_template, redirect, request, url_for, current_app, abort
from flask_login import current_user, login_required


@billing_bp.route('/stripe_pay')
def stripe_pay():
    """Start a checkout session
    Stripe AJAX script will call this endpoint
    """
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1HJt1fA4CgirMDx1YEnD46Uz',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('billing.thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('billing.pricing', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': current_app.config['STRIPE_PUBLIC_KEY']
    }


@billing_bp.route('/pricing')
def pricing():
    return render_template('billing/pricing.html')


@billing_bp.route('/thanks')
def thanks():
    return render_template('billing/thanks.html')
