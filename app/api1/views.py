from flask import render_template, request, redirect, url_for, session, abort, flash, g, jsonify
from . import api1
# from .forms import 
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Comments, Followers, RecModerations, ComModerations
from ..decorators import auth_token_required, is_administrator, admin_token_required, auth_login_required
from .. import db
from ..email import send_email
from datetime import datetime, timedelta
import json
from flask_httpauth import HTTPTokenAuth

@api1.route('/token')
@auth_login_required
def get_token():
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})

@api1.route('/recs/<int:id>/<int:comments>')
@api1.route('/recs/<int:id>')
@auth_token_required
def get_rec(id, comments=False):
    to_ret = Recommendation.query\
        .filter_by(verification=2)\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json(comments))

@api1.route('/users/<int:id>/<int:follow>')
@api1.route('/users/<int:id>')
@auth_token_required
def get_user(id, follow=False):
    to_ret = Users.query\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json(current_user, follow))

@api1.route('/comments/<int:id>')
@auth_token_required
def get_comments(id):
    to_ret = Comments.query\
        .filter_by(verification=2)\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json())

@api1.route('/mod_rec_history/<int:id>/<int:moderated>')
@api1.route('/mod_rec_history/<int:id>')
@admin_token_required
def get_mod_rec_history(id, moderated = -1):
    data = {}
    if moderated != 0:
        data['recs_private'] = {}
    if moderated != 1:
        data['recs_approved'] = {}
    mod = Users.query\
        .filter(Users.role_id != 3)\
        .filter_by(id=id)\
        .first_or_404()
    for x in mod.rec_mods:
        if x.action is True and moderated != 0:
            data['recs_private'][x.mod_on] =  x.rec.text
        elif x.action is False and moderated != 1:
            data['recs_approved'][x.mod_on] = x.rec.text
    return jsonify(data)

@api1.route('/mod_com_history/<int:id>/<int:moderated>')
@api1.route('/mod_com_history/<int:id>')
@admin_token_required
def get_mod_com_history(id, moderated = -1):
    data = {}
    if moderated != 0:
        data['coms_private'] = {}
    if moderated != 1:
        data['coms_approved'] = {}
    mod = Users.query\
        .filter(Users.role_id != 3)\
        .filter_by(id=id)\
        .first_or_404()
    for x in mod.com_mods:
        if x.action is True and moderated != 0:
            data['coms_private'][x.mod_on] =  x.com.comment
        elif x.action is False and moderated != 1:
            data['coms_approved'][x.mod_on] = x.com.comment
    return jsonify(data)

@api1.route('/rec_mods/<int:id>')
@admin_token_required
def get_rec_mods(id):
    to_ret = RecModerations.query\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json())
    
@api1.route('/com_mods/<int:id>')
@admin_token_required
def get_com_mods(id):
    to_ret = ComModerations.query\
        .filter_by(id=id)\
        .first_or_404()
    return jsonify(to_ret.to_json())

@api1.route('/admin')
@admin_token_required
def get_admin():
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
    data['mods'] = {mod.id: mod.username for mod in Users.query.filter_by(role_id = 2)}
    data['mods_count'] = Users.query\
        .filter_by(role_id = 2)\
        .count()
    return jsonify(data)