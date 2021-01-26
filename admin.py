from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import db
from app.models import User, Post, Category


class UserView(ModelView):

    column_exclude_list = ['password_hash', ]

def register(app):

    admin = Admin(app, name='My Blog Admin:', template_mode='bootstrap4')
    admin.add_view(UserView(User, db.session))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Category, db.session))
