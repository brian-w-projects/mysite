from flask import render_template, session, redirect, url_for, request, abort, flash
from . import main
# from .forms import SignUpForm
from .. import db
from ..models import Users, Recommendation, Permission
from flask_login import login_required, current_user
# from ..email import send_email
from ..decorators import admin_required, permission_required
from ..email import send_email

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/highlight/<int:id>')
def highlight(id):
    display_recs = [Recommendation.query.filter_by(id=id).first_or_404()]
    return render_template('highlight.html', display=display_recs)
    