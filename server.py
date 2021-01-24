from app import app, db, moment
from app.models import User, Post, Category


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Category': Category}
