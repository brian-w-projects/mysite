from flask import render_template, request, redirect, url_for, session, abort, flash
from . import admin
# from .forms import 
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Comments, Followers, RecModerations, ComModerations
from ..decorators import is_administrator
from .. import db
from ..email import send_email
from datetime import datetime, timedelta
import json

@admin.route('/splash')
@login_required
@is_administrator
def admin_splash():
    week_ago = datetime.today() - timedelta(days=7)
    data = {}
    data['count'] = Users.query.count()
    data['recent_account'] = Users.query\
        .filter(Users.member_since > week_ago )\
        .count()
    data['recent_logins'] = Users.query\
        .filter(Users.last_login > week_ago)\
        .count()
    data['total_recs'] = Recommendation.query.count()
    data['recent_recs'] = Recommendation.query\
        .filter(Recommendation.timestamp > week_ago)\
        .count()
    data['total_comments'] = Comments.query.count()
    data['recent_comments'] = Comments.query\
        .filter(Comments.timestamp > week_ago)\
        .count()
    data['recs_to_mod'] = Recommendation.query\
        .filter(Recommendation.verification == 1)\
        .count()
    data['comments_to_mod'] = Comments.query\
        .filter_by(verification=1)\
        .count()
    data['mods'] = Users.query\
        .filter_by(role_id = 2)
    data['mods_count'] = data['mods'].from_self()\
        .count()
    return render_template('admin/admin_splash.html', data=data, RecModerations=RecModerations,
        ComModerations=ComModerations, week_ago=week_ago)

@admin.route('/mod_history/<int:id>')
@login_required
@is_administrator
def mod_history(id):
    mod = Users.query\
        .filter(Users.role_id != 3)\
        .filter_by(id=id).first_or_404()
    return render_template('admin/mod_history.html', mod=mod)