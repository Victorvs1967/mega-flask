from flask import render_template, redirect, flash

from app import app
from .forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    title = 'Main Page'
    user = { 'username': 'Victor'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Texas!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Nick'},
            'body': 'Your fish is ugly!'
        },
        {
            'author': {'username': 'Harry'},
            'body': 'I am the best developer!'
        }
    ]
    return render_template('index.html', title=title, user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Sign In'
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data} remember_me={form.remember_me.data}')
        return redirect('/index')
    return render_template('login.html', title=title, form=form)

