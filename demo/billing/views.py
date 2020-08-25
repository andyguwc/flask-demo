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
        cancel_url=url_for('main.index', _external=True),
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


@billing_bp.route('/stripe_webhooks', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_k7WAjFrTNJNyRDKpzBKIKFh5vH0VRBVG'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}