from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, g, current_app
from flask.json import jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import get_locale, _
from werkzeug.urls import url_parse

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, MessageForm
from app.models import User, Post, Category, Message, Notification


@bp.before_request
def before_request():
    g.locale = str(get_locale())
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    title = 'Main Page'
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=title, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore')
@login_required
def explore():
    title = 'Explore'
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=title, posts=posts.items, next_url=next_url, prev_url=prev_url)
    
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    title = 'Edit Profile'
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=title, form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You connot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!')
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}.')
    return redirect(url_for('main.user', username=username))

@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    title = _('Send Message')
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_messages_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been send.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=title, form=form, recipient=recipient)

@bp.route('/message')
@login_required
def messages():
    current_user.last_massage_read_time = datetime.utcnow()
    current_user.add_notification('unread_messages_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(Message.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) if messages.has_prev else None
    return render_template('messages.html', messages=messages.items, next_url=next_url, prev_url=prev_url)

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])

@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash('An export task is currently in progress')
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))
