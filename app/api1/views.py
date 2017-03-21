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

def message(code, message):
    response = jsonify({'Code': code, 'message': message})
    response.status_code = code
    return response

@api1.route('/token')
@auth_login_required
def get_token():
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})

@api1.route('/recs/<int:id>', methods=['GET'])
@auth_token_required
def get_rec(id):
    to_ret = Recommendation.query\
        .filter_by(id=id)\
        .first()
    if not to_ret or to_ret.verification == -1:
        return message(404, 'This rec does not exist')
    elif to_ret.verification == 0 and to_ret.author_id != g.current_user.id:
        return message(403, 'This is not your rec to view')
    else:
        return jsonify(to_ret.to_json())

@api1.route('/recs/<int:id>', methods=['PUT'])
@auth_token_required
def put_rec(id):
    if not request.get_json(silent=True):
        return message(400, 'text, title or public must be present')
    text = request.json.get('text')
    title = request.json.get('title')
    public = request.json.get('public')
    if text is None and title is None and public is None:
        return message(400, 'text, title or public must be present')
    rec = Recommendation.query\
        .filter_by(id=id)\
        .first()
    if not rec:
        return message(404, 'This recommendation does not exist')
    if rec.author_id != g.current_user.id:
        return message(403, 'This is not your rec to edit')
    if text is not None:
        if len(text) <= 500:
            rec.text = text
        else:
            return message(400, 'Max text length is 500')
    if title is not None:
        if len(title) <= 100:
            rec.title = title
        else:
            return message(400, 'Max title length is 100')
    if public is not None:
        if public == 'True':
            rec.verification = 1
        elif public == 'False':
            rec.verification = 0
        else:
            return message(400, 'Public must be True or False')
    db.session.add(rec)
    db.session.commit()
    return message(201, 'Rec succesfully updated')

@api1.route('/recs/<int:id>', methods=['DELETE'])
@auth_token_required
def delete_rec(id):
    rec = Recommendation.query\
        .filter_by(id=id)\
        .first()
    if not rec:
        return message(404, 'This rec does not exist')
    if rec.author_id != g.current_user.id:
        return message(403, 'This rec is not yours to delete')
    rec.verification = -1
    db.session.add(rec)
    db.session.commit()
    return message(201, 'Rec successfully deleted')

@api1.route('/recs', methods=['POST'])
@auth_token_required
def post_rec():
    if not request.get_json(silent=True):
        return message(400, 'text, title and public must be present')
    text = request.json.get('text')
    title = request.json.get('title')
    public = request.json.get('public')
    if text is None or len(text) > 500:
        return message(400, 'Text must be between 1 and 500 characters')
    if title is None or len(title) > 100:
        return message(400, 'Title must be between 1 and 100 characters')
    if public is None or public not in ['True', 'False']:
        return message(400, 'Public must be True or False')
    to_add = Recommendation(title=title, author_id=g.current_user.id, text=text,
        verification=public)
    db.session.add(to_add)
    db.session.commit()
    return message(201, 'Rec successfully posted')

@api1.route('/recs/<int:id>/comments', methods=['GET'])
@auth_token_required
def get_rec_comments(id):
    to_ret = Recommendation.query\
        .filter_by(id=id)\
        .first()
    if not to_ret or to_ret.verification == -1:
        return message(404, 'This rec does not exist')
    elif to_ret.verification == 0 and to_ret.author_id != g.current_user.id:
        return message(403, 'This is not your rec to view')
    else:
        return jsonify(to_ret.to_json_comments())

@api1.route('/recs/<int:id>/comments', methods=['POST'])
@auth_token_required
def post_rec_comments(id):
    if not request.get_json(silent=True):
        return message(400, 'text must be present')
    text = request.json.get('text')
    if text is None or len(text) > 250:
        return message(400, 'text must be between 1 and 250 characters')
    to_ret = Recommendation.query\
        .filter_by(id=id)\
        .first()
    if not to_ret or to_ret.verification == -1:
        return message(404, 'This rec does not exist')
    elif to_ret.verification == 0 and to_ret.author_id != g.current_user.id:
        return message(403, 'Comments may not be posed on this rec')
    to_add = Comments(comment_by=g.current_user.id, posted_on=id, comment=text)
    db.session.add(to_add)
    db.session.commit()
    return message(201, 'Comment successfully posted')

@api1.route('/comments/<int:id>', methods=['GET'])
@auth_token_required
def get_comments(id):
    to_ret = Comments.query\
        .filter(Comments.verification > 0)\
        .filter_by(id=id)\
        .first()
    if not to_ret:
        return message(404, 'This comment does not exist')
    return jsonify(to_ret.to_json())

@api1.route('/comments/<int:id>', methods=['PUT'])
@auth_token_required
def edit_comments(id):
    com = Comments.query\
        .filter(Comments.verification > 0)\
        .filter_by(id=id)\
        .first()
    if not com:
        return message(404, 'This comment does not exist')
    if com.comment_by != g.current_user.id:
        return message(403, 'This comment is not your to edit')
    if not request.get_json(silent=True):
        return message(400, 'text must be present')
    text = request.json.get('text')
    if text is None or len(text) > 250:
        return message(400, 'Comment text must be between 1 and 250 characters')
    com.comment = text
    db.session.add(com)
    db.session.commit()
    return message(201, 'Comment successfully edited')

@api1.route('/comments/<int:id>', methods=['DELETE'])
@auth_token_required
def delete_comments(id):
    com = Comments.query\
        .filter(Comments.verification > 0)\
        .filter_by(id=id)\
        .first()
    if not com:
        return message(404, 'This comment does not exist')
    if com.comment_by != g.current_user.id and com.posted.author_id != g.current_user.id:
        return message(403, 'This comment is not your to delete')
    com.verification = 0
    db.session.add(com)
    db.session.commit()
    return message(201, 'Comment successfully deleted')

@api1.route('/users/<int:id>', methods=['GET'])
@auth_token_required
def get_user(id):
    to_ret = Users.query\
        .filter_by(id=id)\
        .first()
    if not to_ret:
        return message(404, 'This user does not exist')
    return jsonify(to_ret.to_json())

@api1.route('/users', methods=['PUT'])
@auth_token_required
def put_user():
    if not request.get_json(silent=True):
        return message(400, 'Must provide value for display, about_me or updates')
    display = request.json.get('display')
    about_me = request.json.get('about_me')
    updates = request.json.get('updates')
    if display is None and about_me is None and updates is None:
        return message(400, 'Must provide value for display, about_me or updates')
    if display is not None:
        if display not in ['10', '20', '50']:
            return message(400, 'Display must be 10, 20 or 50')
        else:
            g.current_user.display = int(display)
    if about_me is not None:
        if len(about_me) > 500:
            return message(400, 'Max length of about_me is 1000 characters')
        else:
            g.current_user.about_me = about_me
    if updates is not None:
        if updates == 'True':
            g.current_user.updates = 1
        elif updates == 'False':
            g.current_user.updates = 0
        else:
            return message(400, 'Updates must be either True or False')
    db.session.add(g.current_user)
    db.session.commit()
    return message(201, 'User successfully updated')

@api1.route('/users/<int:id>/following', methods=['GET'])
@auth_token_required
def get_user_following(id):
    to_ret = Users.query\
        .filter_by(id=id)\
        .first()
    if not to_ret:
        return message(404, 'This user does not exist')
    return jsonify(to_ret.to_json_following())

@api1.route('/users/<int:id>/followed_by', methods=['GET'])
@auth_token_required
def get_user_followed_by(id):
    to_ret = Users.query\
        .filter_by(id=id)\
        .first()
    if not to_ret:
        return message(404, 'This user does not exist')
    return jsonify(to_ret.to_json_followed())

@api1.route('/follow/<int:id>', methods=['PUT'])
@auth_token_required
def put_follower(id):
    user = Users.query\
        .filter_by(id=id)\
        .first()
    if not user:
        return message(404, 'This user does not exist')
    if id == g.current_user.id:
        return message(400, 'You may not follow yourself')
    if g.current_user.following.filter_by(following=id).first():
        return message(400, 'You are already following this user')
    else:
        to_add = Followers(follower=g.current_user.id, following=id)
        db.session.add(to_add)
        db.session.commit()
        return message(201, 'Succesfully following user')

@api1.route('/unfollow/<int:id>', methods=['DELETE'])
@auth_token_required
def delete_follow(id):
    user = Users.query\
        .filter_by(id=id)\
        .first()
    if not user:
        return message(404, 'This user does not exist')
    if id == g.current_user.id:
        return message(400, 'You may not unfollow yourself')
    f = g.current_user.following.filter_by(following=user.id).first()
    if not f:
        return message(400, 'You are not following this user')
    else:
        db.session.delete(f)
        db.session.commit()
        return message(201, 'Successfully unfollowed user')

# Stopped Here on Monday

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
        .first()
    if not mod:
        return message(404, 'This moderator does not exist')
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
        .first()
    if not mod:
        return message(404, 'This moderator does not exist')
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
        .first()
    if not to_ret:
        return message(404, 'This Rec Moderation does not exist')
    return jsonify(to_ret.to_json())
    
@api1.route('/com_mods/<int:id>')
@admin_token_required
def get_com_mods(id):
    to_ret = ComModerations.query\
        .filter_by(id=id)\
        .first()
    if not to_ret:
        return message(404, 'This Comment Moderation does not exist')
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