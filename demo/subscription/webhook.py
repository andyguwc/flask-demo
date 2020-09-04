import stripe
import datetime 

from . import stripe_webhook_bp
from flask import render_template, redirect, request, url_for, current_app, abort, flash
from demo.models import Subscription, User, Invoice
from demo.extensions import db

 
@stripe_webhook_bp.route('/event', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
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
        data = event['data']['object']
        parsed_info = {
            'user_id': data['client_reference_id'],
            'stripe_customer_id': data['customer'],
        }
        # first link the stripe customer to the user
        User.parse_event_checkout_completed(parsed_info)
                
        # then create the subscription object
        subscription_data = stripe.Subscription.retrieve(data['subscription'])
        
        subscription = Subscription(
            user_id=data['client_reference_id'],
            plan=subscription_data['plan']['id']
        )
        db.session.add(subscription)
        db.session.commit()

    # Handle invoice.paid event
    if event['type'] == 'invoice.paid':
        data = event['data']['object']

        plan_info = data['lines']['data'][0]['plan']

        period_start_on = datetime.datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['start']).date()
        period_end_on = datetime.datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['end']).date()

        parsed_info = {
            'payment_id': data['customer'],
            'plan': plan_info['id'],
            'receipt_number': data['receipt_number'],
            'description': plan_info['nickname'],
            'period_start_on': period_start_on,
            'period_end_on': period_end_on,
            'currency': data['currency'],
            'tax': data['tax'],
            'tax_percent': data['tax_percent'],
            'total': data['total'],
        }

        Invoice.parse_event_save_invoice(parsed_info)

    return {}
