# -*- coding: utf-8 -*-
import click
import os

from flask_migrate import upgrade
from flask.cli import with_appcontext

from demo.models import Role

@click.command()
@with_appcontext
def deploy():
    """Run deployment tasks."""
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


@click.command()
def comment_test():
    """Test comment"""
    # add command group here https://flask.palletsprojects.com/en/0.12.x/cli/
    click.echo('Some command here')
