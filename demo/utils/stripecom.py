# -*- coding: utf-8 -*-
import stripe


class Event(object):
    @classmethod
    def retrieve(cls, event_id):
        """
        Retrieve an event, this is used to validate the event in attempt to
        protect us from potentially malicious events not sent from Stripe.

        API Documentation:
          https://stripe.com/docs/api#retrieve_event

        :param event_id: Stripe event id
        :type event_id: int
        :return: Stripe event
        """
        return stripe.Event.retrieve(event_id)


class Card(object):
    @classmethod
    def update(cls, customer_id, stripe_token=None):
        """
        Update an existing card through a customer.

        API Documentation:
          https://stripe.com/docs/api/python#update_card

        :param customer_id: Stripe customer id
        :type customer_id: int
        :param stripe_token: Stripe token
        :type stripe_token: str
        :return: Stripe customer
        """
        customer = stripe.Customer.retrieve(customer_id)
        customer.source = stripe_token

        return customer.save()


class Invoice(object):
    @classmethod
    def upcoming(cls, customer_id):
        """
        Retrieve an upcoming invoice item for a user.

        API Documentation:
          https://stripe.com/docs/api#retrieve_customer_invoice

        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe invoice
        """
        return stripe.Invoice.upcoming(customer=customer_id)


class Subscription(object):
    @classmethod
    def create(cls, token=None, email=None, plan=None):
        """
        Create a new subscription.

        API Documentation:
          https://stripe.com/docs/api#create_subscription

        :param token: Token returned by JavaScript
        :type token: str
        :param email: E-mail address of the customer
        :type email: str
        :param plan: Plan identifier
        :type plan: str
        :return: Stripe customer
        """
        params = {
            'source': token,
            'email': email,
            'plan': plan
        }

        return stripe.Customer.create(**params)

    @classmethod
    def update(cls, customer_id=None, plan=None):
        """
        Update an existing subscription.

        API Documentation:
          https://stripe.com/docs/api/python#update_subscription

        :param customer_id: Customer id
        :type customer_id: str
        :param plan: Plan identifier
        :type plan: str
        :return: Stripe subscription
        """
        customer = stripe.Customer.retrieve(customer_id)
        subscription_id = customer.subscriptions.data[0].id
        subscription = customer.subscriptions.retrieve(subscription_id)

        subscription.plan = plan

        return subscription.save()

    @classmethod
    def cancel(cls, customer_id=None):
        """
        Cancel an existing subscription.

        API Documentation:
          https://stripe.com/docs/api#cancel_subscription

        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe subscription object
        """
        customer = stripe.Customer.retrieve(customer_id)
        subscription_id = customer.subscriptions.data[0].id

        return customer.subscriptions.retrieve(subscription_id).delete()


class Plan(object):
    @classmethod
    def retrieve(cls, plan):
        """
        Retrieve an existing plan.

        API Documentation:
          https://stripe.com/docs/api#retrieve_plan

        :param plan: Plan identifier
        :type plan: str
        :return: Stripe plan
        """
        try:
            return stripe.Plan.retrieve(plan)
        except stripe.error.StripeError as e:
            print(e)

    @classmethod
    def list(cls):
        """
        List all plans.

        API Documentation:
          https://stripe.com/docs/api#list_plans

        :return: Stripe plans
        """
        try:
            return stripe.Plan.list()
        except stripe.error.StripeError as e:
            print(e)

    @classmethod
    def create(cls, id=None, name=None, amount=None, currency=None,
               interval=None, interval_count=None, trial_period_days=None):
        """
        Create a new plan.
        https://stripe.com/docs/api#create_plan
        """
        try:
            return stripe.Plan.create(id=id,
                                      nickname=name,
                                      product={
                                        'name': 'Subscription',
                                      },
                                      amount=amount,
                                      currency=currency,
                                      interval=interval,
                                      interval_count=interval_count,
                                      trial_period_days=trial_period_days)
        except stripe.error.StripeError as e:
            print(e)

    @classmethod
    def update(cls, id=None, name=None):
        """
        Update an existing plan.
        https://stripe.com/docs/api#update_plan
        """
        try:
            plan = stripe.Plan.retrieve(id)

            plan.nickname = name
            return plan.save()
        except stripe.error.StripeError as e:
            print(e)

    @classmethod
    def delete(cls, plan):
        """
        Delete an existing plan.

        API Documentation:
          https://stripe.com/docs/api#delete_plan

        :param plan: Plan identifier
        :type plan: str
        :return: Stripe plan object
        """
        try:
            plan = stripe.Plan.retrieve(plan)
            return plan.delete()
        except stripe.error.StripeError as e:
            print(e)
