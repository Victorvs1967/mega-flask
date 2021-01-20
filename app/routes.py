from flask import render_template

from app import app


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
