import stripe

from . import subscription_bp
from flask import render_template, redirect, request, url_for, current_app, abort, flash
from flask_login import current_user, login_required
from demo.models import Subscription, Invoice


@subscription_bp.route('/pricing')
def pricing():
    # if already has subscription, return to billing details page
    if current_user.is_authenticated and current_user.subscription:
        return redirect(url_for('subscription.billing_details'))

    return render_template('subscription/pricing.html', 
                            plans=current_app.config['STRIPE_PLANS'])


@login_required
@subscription_bp.route('/stripe_pay')
def stripe_pay():
    """Start a checkout session
    Stripe AJAX script will call this endpoint
    """
    # /stripe_pay?plan=platinum
    plan = request.args.get('plan')
    
    # https://stripe.com/docs/api/checkout/sessions/object
    # pass client_reference_id and customer to tie this session with stripe customer
    session = stripe.checkout.Session.create(
        client_reference_id=current_user.id,
        customer=current_user.payment_id or None,
        payment_method_types=['card'],
        line_items=[{
            'price': plan,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=url_for('subscription.thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('subscription.pricing', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': current_app.config['STRIPE_PUBLIC_KEY']
    }


@subscription_bp.route('/thanks')
def thanks():
    return render_template('subscription/thanks.html')


@subscription_bp.route('/billing_details')
@login_required
def billing_details():
    """View billing history and upcoming invoce from the subscription
    """
    invoices = Invoice.billing_history(current_user)
    if current_user.subscription:
        upcoming = Invoice.upcoming(current_user.payment_id)
    else:
        upcoming = None
    return render_template('subscription/billing_details.html', invoices=invoices, upcoming=upcoming)


@subscription_bp.route('/cancel', methods=['GET', 'POST'])
@login_required
def cancel():
    pass


@subscription_bp.route('/update_payment_method', methods=['GET', 'POST'])
@login_required
def update_payment_method():
    pass


