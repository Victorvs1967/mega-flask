from flask import Blueprint


bp = Blueprint('admins', __name__)

from app.admin import admin