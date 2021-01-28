from app import create_app, db, cli
from app.models import User, Post, Category, Message, Notification, Task


app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Category': Category, 'Message': Message, 'Notification': Notification, 'Task': Task}
