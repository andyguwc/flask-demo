# -*- coding: utf-8 -*-
import click
import os

from flask_migrate import upgrade
from flask import current_app
from flask.cli import with_appcontext, AppGroup

from demo.models import Role
from demo.extensions import db


"""
Additional Flask Commands
"""


@click.command()
@with_appcontext
def deploy():
    """Run deployment tasks. Called upon app initialization
    """
    # migrate database to latest revision
    upgrade()

    # create or update user roles
    Role.insert_roles()


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, _, filenames in os.walk('.'):
        if 'venv' in dirpath:
            continue
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)


# add stripe commands
stripe_cli = AppGroup('stripe')


@stripe_cli.command()
def sync_plans():
    """
    Sync (upsert) STRIPE_PLANS to Stripe.

    :return: None
    """
    if current_app.config['STRIPE_PLANS'] is None:
        return None

    for _, value in current_app.config['STRIPE_PLANS'].items():
        try:
            plan = stripe.Plan.retrieve(value.get('id'))
            if plan:
                plan.nickname = value.get('nickname')
                plan.save()
            else:
                stripe.Plan.create(product={'name': 'Subscription'}, **value)
        except stripe.error.StripeError as e:
            print(e)

    return None


@stripe_cli.command()
def list_plans():
    """
    List all existing plans on Stripe.

    :return: Stripe plans
    """
    click.echo(stripe.Plan.list())