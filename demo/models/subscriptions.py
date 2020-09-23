# -*- coding: utf-8 -*-
import stripe
from datetime import datetime
from flask import current_app

from .mixins import ResourceMixin
from demo.extensions import db, login_manager


class Subscription(ResourceMixin, db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', 
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)
    plan = db.Column(db.String(128))


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

