from flask import render_template, request, redirect, url_for, session, abort, flash, g, jsonify
from . import api1
# from .forms import 
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Comments, Followers, RecModerations, ComModerations
from ..decorators import auth_token_required, is_administrator
from .. import db
from ..email import send_email
from datetime import datetime, timedelta
import json

@api1.route('/token')
@login_required
def get_token():
    return jsonify({'token': current_user.generate_auth_token(expiration=3600), 'expiration': 3600})

@api1.route('/recs/token=<string:token>&id=<int:id>&comments=<int:comments>')
@api1.route('/recs/token=<string:token>&id=<int:id>')
@auth_token_required
def get_rec(token, id, comments=False):
    to_ret = Recommendation.query\
        .filter_by(verification=2)\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json(comments))

@api1.route('/users/token=<string:token>&id=<int:id>&follow=<int:follow>')
@api1.route('/users/token=<string:token>&id=<int:id>')
@auth_token_required
def get_user(token, id, follow=False):
    to_ret = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json(current_user, follow))

@api1.route('/comments/token=<string:token>&id=<int:id>')
@auth_token_required
def get_comments(token, id):
    to_ret = Comments.query\
        .filter_by(verification=2)\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json())

@api1.route('/rec_mods/token=<string:token>&id=<int:id>')
@auth_token_required
@is_administrator
def get_rec_mods(token, id):
    to_ret = RecModerations.query\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json())
    
@api1.route('/com_mods/token=<string:token>&id=<int:id>')
@auth_token_required
@is_administrator
def get_com_mods(token, id):
    to_ret = ComModerations.query\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json())

@api1.route('/admin/token=<string:token>')
@auth_token_required
@is_administrator
def get_admin(token):
    week_ago = datetime.today() - timedelta(days=7)
    data = {}
    data['total_accounts'] = Users.query.count()
    data['recent_accounts'] = Users.query\
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
    mod_add = {mod.id: mod.username for mod in Users.query.filter_by(role_id = 2)}
    data['mods'] = mod_add
    data['mods_count'] = Users.query\
        .filter_by(role_id = 2)\
        .count()
    return jsonify(data)