from flask_admin.contrib.sqla import ModelView

from app import db, admin
from app.models import User, Post, Category, Message, Notification, Task


class UserView(ModelView):   
    column_exclude_list = ['password_hash', ]

admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Message, db.session))
admin.add_view(ModelView(Notification, db.session))
admin.add_view(ModelView(Task, db.session))
