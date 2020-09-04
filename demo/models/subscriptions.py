# -*- coding: utf-8 -*-
import stripe
from datetime import datetime
from flask import current_app

from .mixins import ResourceMixin
from demo.extensions import db, login_manager
from demo.utils.stripecom import Subscription as PaymentSubscription
from demo.utils.stripecom import Card as PaymentCard


class Subscription(ResourceMixin, db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', 
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)
    plan = db.Column(db.String(128))
    
    def update(self, user, plan):
        """Update an existing subscription
        """
        PaymentSubscription.update(user.payment_id, plan)
        user.subscription.plan = plan
        db.session.add(user.subscription)
        db.session.commit()

        return True
    
    def cancel(self, user, discard_credit_card=True):
        """Cancel an existing subscription
        """
        PaymentSubscription.cancel(user.payment_id)
        user.payment_id = None
        user.cancelled_subscription_on = datetime.utcnow()
        
        db.session.add(user)
        db.session.delete(user.subscription)

        db.session.commit()

        return True


class Invoice(ResourceMixin, db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', 
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)
    
    plan = db.Column(db.String(128))
    receipt_number = db.Column(db.String(128))
    description = db.Column(db.String(128))
    period_start_on = db.Column(db.Date)
    period_end_on = db.Column(db.Date)
    currency = db.Column(db.String(8))
    tax = db.Column(db.Integer)
    tax_percent = db.Column(db.Float())
    total = db.Column(db.Integer)

    # denormalizes the card details 
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date)

    @classmethod
    def billing_history(cls, user):
        """Get all invoices for a user
        """
        invoices = cls.query.filter(cls.user_id == user.id) \
            .order_by(cls.created_on.desc()).limit(12)
        return invoices

    @classmethod
    def parse_from_event(cls, payload):
        """
        Parse and return the invoice information that will get saved locally.

        :return: dict
        """
        data = payload['data']['object']
        plan_info = data['lines']['data'][0]['plan']

        period_start_on = datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['start']).date()
        period_end_on = datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['end']).date()

        invoice = {
            'payment_id': data['customer'],
            'plan': plan_info['name'],
            'receipt_number': data['receipt_number'],
            'description': plan_info['statement_descriptor'],
            'period_start_on': period_start_on,
            'period_end_on': period_end_on,
            'currency': data['currency'],
            'tax': data['tax'],
            'tax_percent': data['tax_percent'],
            'total': data['total']
        }

        return invoice


    @classmethod
    def parse_event_save_invoice(cls, parsed_event):
        """Save invoice after parsing from event
        """
        # import from User and avoid circular imports
        from .users import User

        # only save invoice if the user is valid
        id = parsed_event.get('payment_id')
        user = User.query.filter((User.payment_id == id)).first()

        if user:
            parsed_event['user_id'] = user.id
            # parsed_event['brand'] = user.credit_card.brand
            # parsed_event['last4'] = user.credit_card.last4
            # parsed_event['exp_date'] = user.credit_card.exp_date

            del parsed_event['payment_id']

            invoice = Invoice(**parsed_event)
            invoice.save()

        return user

    @classmethod
    def upcoming(cls, customer_id):
        """Upcoming invoice item 
        """
        payload = stripe.Invoice.upcoming(customer=customer_id)
        line_info = payload['lines']['data'][0]
        plan_info = line_info['plan']
        next_billing_date = datetime.utcfromtimestamp(line_info['period']['start'])

        invoice = {
            'plan': plan_info['id'],
            'description': line_info['description'],
            'next_bill_on': next_billing_date,
            'amount_due': payload['amount_due'],
            'interval': plan_info['interval']
        }

        return invoice


class CreditCard(ResourceMixin, db.Model):
    IS_EXPIRING_THRESHOLD_MONTHS = 2

    __tablename__ = 'credit_cards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)
    # card details
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date, index=True)
    is_expiring = db.Column(db.Boolean(), nullable=False, default=False)

    @classmethod
    def is_expiring_soon(cls, compare_date=None, exp_date=None):
        """Determine whether the credit card is expiring soon
        """
        return cls.IS_EXPIRING_THRESHOLD_MONTHS >= (
            (compare_date.year - exp_date.year)*12 + \
            (compare_date.month - exp_date.month)
        )

    @classmethod
    def extract_card_params(cls, customer):
        """Extract card info from a payment customer object
        """
        card_data = customer.source.data[0]
        exp_date = datetime.date(card_data.exp_year, card_data.exp_month, 1)

        return {
            'brand': card_data.brand,
            'last4': card_data.last4,
            'exp_date': exp_date,
            'is_expiring': cls.is_expiring_soon(exp_date=exp_date)
        }
