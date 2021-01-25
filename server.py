from app import create_app, db, cli, admin
from app.models import User, Post, Category


app = create_app()
cli.register(app)
admin.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Category': Category}
