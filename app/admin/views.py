from flask import render_template, request, redirect, url_for, session, abort, flash
from . import admin
# from .forms import 
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Permission, Comments, Followers, RecModerations, ComModerations
from ..decorators import permission_required
from .. import db
from ..email import send_email
from datetime import datetime, timedelta
import json

@admin.route('/admin')
@login_required
@permission_required(Permission.ADMINISTER)
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
        .filter_by(verification=1)\
        .count()
    data['comments_to_mod'] = Comments.query\
        .filter_by(verified=False)\
        .count()
    data['mods'] = Users.query\
        .filter_by(role_id = 1)
    data['mods_count'] = data['mods'].from_self()\
        .count()
    return render_template('admin/admin_splash.html', data=data, RecModerations=RecModerations,
        ComModerations=ComModerations, week_ago=week_ago)