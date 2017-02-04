from flask import render_template, session, redirect, url_for, request, abort
from . import main
# from .forms import MyForm, EditProfilePage, PostForm
from .. import db
# from ..models import Users, Tokens, Permission, Post
from flask_login import login_required, current_user
# from ..email import send_email
from ..decorators import admin_required, permission_required

@main.route('/')
def index():
    return render_template('index.html')

