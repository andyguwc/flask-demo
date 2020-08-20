from flask import render_template, redirect, request, url_for, jsonify, flash, abort, current_app
from flask_login import login_required, current_user

from . import main_bp
from .forms import EditProfileForm, PostForm, EditPostForm
from demo.models import User, Post, Permission
from demo.extensions import db
from demo.tasks.long_task import long_task
from demo.utils.auth import admin_required, moderate_required


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, 
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('main/index.html', form=form, posts=posts, pagination=pagination)


@main_bp.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('main/user.html', user=user, posts=posts)


@main_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated')
        return redirect(url_for('main.user', username=current_user.username))
    # initialize fields as current data
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form)


# view a post by id
@main_bp.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('main/post.html', posts=[post])


# edit a post
@main_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author or not current_user.can(Permission.WRITE):
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('Your post has been updated')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    return render_template('main/edit_post.html', form=form) 



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