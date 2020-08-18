from flask import render_template, redirect, request, url_for, jsonify

from . import main_bp
from demo.models import User
from demo.extensions import db
from demo.tasks.long_task import long_task
from demo.utils.auth import admin_required, moderate_required
from flask_login import login_required

@main_bp.route('/')
def index():
    return render_template('main/index.html')


"""
Routes below are for testing purposes
"""

@main_bp.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'Admin Only'

# test route for long running tasks
@main_bp.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('main.taskstatus',
                                                  task_id=task.id)}

@main_bp.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)