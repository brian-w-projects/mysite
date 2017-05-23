from flask import g, jsonify, request
from . import api1
from .. import db
from ..decorators import admin_token_required, auth_login_required, auth_request, auth_token_required, moderator_token_required
from ..models import Comment, Com_Moderation, Relationship, Rec_Moderation, Recommendation, User
from datetime import datetime, timedelta
from sqlalchemy import case
from sqlalchemy.sql.expression import asc, desc, distinct, func

def message(code, message):
    response = jsonify({'Code': code, 'message': message})
    response.status_code = code
    return response

@api1.route('/token')
@auth_login_required
def get_token():
    if not g.current_user.api:
        g.current_user.generate_auth_token()
    return jsonify({'token': g.current_user.api})

@api1.route('/token/new')
@auth_login_required
def get_new_token():
    return jsonify({'token': g.current_user.generate_auth_token()})

@api1.route('/recs/<int:id>', methods=['GET'])
@auth_token_required
@auth_request(role=3)
def get_rec(id):
    to_ret = Recommendation.query\
        .get(int(id))
    if not to_ret or to_ret.verification == -1:
        return message(404, 'This rec does not exist')
    elif to_ret.verification == 0 and to_ret.user_id != g.current_user.id:
        return message(403, 'This is not your rec to view')
    else:
        return jsonify({to_ret.id: to_ret.to_json()})

@api1.route('/recs/<int:id>', methods=['PUT'])
@auth_token_required
@auth_request(role=3)
def put_rec(id):
    if not request.get_json(silent=True):
        return message(400, 'text, title or public must be present')
    text = request.json.get('text')
    title = request.json.get('title')
    public = request.json.get('public')
    if text is None and title is None and public is None:
        return message(400, 'text, title or public must be present')
    rec = Recommendation.query\
        .get(int(id))
    if not rec or rec.verification == -1:
        return message(404, 'This recommendation does not exist')
    if rec.user_id != g.current_user.id:
        return message(403, 'This is not your rec to edit')
    if text is not None:
        if len(text) <= 1000:
            rec.text = text
        else:
            return message(400, 'Max text length is 1000')
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
@auth_request(role=3)
def delete_rec(id):
    rec = Recommendation.query\
        .get(int(id))
    if not rec or rec.verification == -1:
        return message(404, 'This rec does not exist')
    if rec.user_id != g.current_user.id:
        return message(403, 'This rec is not yours to delete')
    rec.verification = -1
    db.session.add(rec)
    db.session.commit()
    return message(201, 'Rec successfully deleted')

@api1.route('/recs', methods=['POST'])
@auth_token_required
@auth_request(role=3)
def post_rec():
    if not request.get_json(silent=True):
        return message(400, 'text, title and public must be present')
    text = request.json.get('text')
    title = request.json.get('title')
    public = request.json.get('public')
    if text is None or len(text) > 1000:
        return message(400, 'Text must be between 1 and 1000 characters')
    if title is None or len(title) > 100:
        return message(400, 'Title must be between 1 and 100 characters')
    if public is None or public not in ['True', 'False']:
        return message(400, 'Public must be True or False')
    to_add = Recommendation(title=title, user_id=g.current_user.id, text=text,
        verification=public)
    db.session.add(to_add)
    db.session.commit()
    return message(201, 'Rec successfully posted')

@api1.route('/recs/<int:id>/comments', methods=['GET'])
@api1.route('/recs/<int:id>/comments/page/<int:page>')
@auth_token_required
@auth_request(role=3)
def get_rec_comments(id, page=1):
    rec = Recommendation.query\
        .get(int(id))
    if not rec or rec.verification == -1:
        return message(404, 'This rec does not exist')
    elif rec.verification == 0 and rec.user_id != g.current_user.id:
        return message(403, 'This is not your rec to view')
    else:
        to_ret = rec.comment\
            .paginate(page, per_page=g.current_user.display, error_out=False)
        return jsonify({com.id: com.to_json() for com in to_ret.items if com.verification>0})

@api1.route('/recs/<int:id>/comments', methods=['POST'])
@auth_token_required
@auth_request(role=3)
def post_rec_comments(id):
    if not request.get_json(silent=True):
        return message(400, 'text must be present')
    text = request.json.get('text')
    if text is None or len(text) > 250:
        return message(400, 'text must be between 1 and 250 characters')
    to_ret = Recommendation.query\
        .get(int(id))
    if not to_ret or to_ret.verification == -1:
        return message(404, 'This rec does not exist')
    elif to_ret.verification == 0 and to_ret.user_id != g.current_user.id:
        return message(403, 'Comments may not be posed on this rec')
    to_add = Comment(user_id=g.current_user.id, recommendation_id=id, text=text)
    db.session.add(to_add)
    db.session.commit()
    return message(201, 'Comment successfully posted')

@api1.route('/comments/<int:id>', methods=['GET'])
@auth_token_required
@auth_request(role=3)
def get_comments(id):
    to_ret = Comment.query\
        .filter(Comment.verification>0, Comment.id==id)\
        .first()
    if not to_ret:
        return message(404, 'This comment does not exist')
    return jsonify({to_ret.id: to_ret.to_json()})

@api1.route('/comments/<int:id>', methods=['PUT'])
@auth_token_required
@auth_request(role=3)
def edit_comments(id):
    com = Comment.query\
        .filter(Comment.verification>0, Comment.id==id)\
        .first()
    if not com:
        return message(404, 'This comment does not exist')
    if com.user_id != g.current_user.id:
        return message(403, 'This comment is not your to edit')
    if not request.get_json(silent=True):
        return message(400, 'text must be present')
    text = request.json.get('text')
    if text is None or len(text) > 250:
        return message(400, 'Comment text must be between 1 and 250 characters')
    com.text = text
    db.session.add(com)
    db.session.commit()
    return message(201, 'Comment successfully edited')

@api1.route('/comments/<int:id>', methods=['DELETE'])
@auth_token_required
@auth_request(role=3)
def delete_comments(id):
    com = Comment.query\
        .filter(Comment.verification>0, Comment.id==id)\
        .first()
    if not com:
        return message(404, 'This comment does not exist')
    if com.user_id != g.current_user.id and com.recommendation.user_id != g.current_user.id:
        return message(403, 'This comment is not your to delete')
    com.verification = -1
    db.session.add(com)
    db.session.commit()
    return message(201, 'Comment successfully deleted')

@api1.route('/users/<int:id>', methods=['GET'])
@auth_token_required
@auth_request(role=3)
def get_user(id):
    to_ret = User.query\
        .get(int(id))
    if to_ret is None:
        return message(404, 'This user does not exist')
    return jsonify(to_ret.to_json())

@api1.route('/users/<int:id>/recs', methods=['GET'])
@api1.route('/users/<int:id>/recs/page/<int:page>', methods=['GET'])
@auth_token_required
def get_user_recs(id, page=1):
    user = User.query\
        .get(int(id))
    if user is None:
        return message(404, 'This user does not exist')
    if g.current_user.id == id:
        private = 0
    else:
        private = 1
    recs = Recommendation.query\
        .filter(Recommendation.user_id==id, Recommendation.verification>=private)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    return jsonify({x.id: x.to_json() for x in recs.items})

@api1.route('/users/<int:id>/comments', methods=['GET'])
@api1.route('/users/<int:id>/comments/page/<int:page>', methods=['GET'])
@auth_token_required
@auth_request(role=3)
def get_user_comments(id, page=1):
    user = User.query\
        .get(int(id))
    if user is None:
        return message(404, 'This user does not exist')
    comments = Comment.query\
        .filter(Comment.user_id==id, Comment.verification>0)\
        .order_by(desc(Comment.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    return jsonify({com.id : com.to_json() for com in comments.items})

@api1.route('/users', methods=['PUT'])
@auth_token_required
@auth_request(role=3)
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
            return message(400, 'Max length of about_me is 500 characters')
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
@auth_request(role=3)
def get_user_following(id):
    to_ret = User.query\
        .get(int(id))
    if to_ret is None:
        return message(404, 'This user does not exist')
    return jsonify(to_ret.to_json_following())

@api1.route('/users/<int:id>/followed_by', methods=['GET'])
@auth_token_required
@auth_request(role=3)
def get_user_followed_by(id):
    to_ret = User.query\
        .get(int(id))
    if to_ret is None:
        return message(404, 'This user does not exist')
    return jsonify(to_ret.to_json_followed())

@api1.route('/follow/<int:id>', methods=['POST'])
@auth_token_required
@auth_request(role=3)
def put_follower(id):
    user = User.query\
        .get(int(id))
    if user is None:
        return message(404, 'This user does not exist')
    if id == g.current_user.id:
        return message(400, 'You may not follow yourself')
    if g.current_user.following.filter_by(following=id).first():
        return message(400, 'You are already following this user')
    else:
        to_add = Relationship(follower=g.current_user.id, following=id)
        db.session.add(to_add)
        db.session.commit()
        return message(201, 'Succesfully following user')

@api1.route('/follow/<int:id>', methods=['DELETE'])
@auth_token_required
@auth_request(role=3)
def delete_follow(id):
    user = User.query\
        .get(int(id))
    if user is None:
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

@api1.route('/search/recs', methods=['GET'])
@api1.route('/search/recs/page/<int:page>', methods=['GET'])
@auth_token_required
@auth_request(role=3)
def get_search_recs(page = 1):
    display_recs = Recommendation.query\
        .join(User)\
        .filter(Recommendation.verification > 0)
    if request.args.get('term', None) is not None:
        display_recs = display_recs\
            .filter(Recommendation.title.contains(request.args.get('term')))
    if request.args.get('user', None) is not None:
        display_recs = display_recs\
            .filter(User.username.contains(request.args.get('user')))
    if request.args.get('date', None) is not None:
        date =  datetime.strptime(request.args.get('date'), '%m/%d/%Y') + timedelta(days=1)
        display_recs = display_recs\
            .filter(Recommendation.timestamp<=date)
    display_recs = display_recs\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    return jsonify({x.id : x.to_json() for x in display_recs.items})

@api1.route('/search/comments', methods=['GET'])
@api1.route('/search/comments/page/<int:page>', methods=['GET'])
@auth_token_required
@auth_request(role=3)
def get_search_comments(page = 1):
    display_comments = Comment.query\
        .join(User)\
        .filter(Comment.verification>0)
    if request.args.get('term', None) is not None:
        display_comments = display_comments\
            .filter(Comment.comment.contains(request.json.get('term')))
    if request.args.get('user', None) is not None:
        display_comments = display_comments\
            .filter(User.username.contains(request.json.get('user')))
    if request.args.get('date', None) is not None:
        date =  datetime.strptime(request.json.get('date'), '%m/%d/%Y') + timedelta(days=1)
        display_comments = display_comments\
            .filter(Comment.timestamp<=date)
    display_comments = display_comments\
        .order_by(desc(Comment.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    return jsonify({x.id: x.to_json() for x in display_comments.items})

@api1.route('/admin')
@admin_token_required
@auth_request(role=1)
def get_admin():
    week_ago = datetime.today() - timedelta(days=7)
    data = {}
    
    users = func.count(distinct(User.id))
    recent_users = func.count(distinct(case([(User.member_since>week_ago, User.id),])))
    recent_logins = func.count(distinct(case([(User.last_login>week_ago, User.id),])))
    data['users'], data['recent_users'], data['recent_logins'] = db.session\
        .query(users, recent_users, recent_logins)\
        .all()[0]

    recs = func.count(distinct(Recommendation.id))
    recent_recs = func.count(distinct(case([(Recommendation.timestamp>week_ago, Recommendation.id),])))
    unverified_recs = func.count(distinct(case([(Recommendation.verification==1, Recommendation.id),])))
    data['recs'], data['recent_recs'], data['unverified_recs'] = db.session\
        .query(recs, recent_recs, unverified_recs)\
        .all()[0]
    
    comments = func.count(distinct(Comment.id))
    recent_comments = func.count(distinct(case([(Comment.timestamp>week_ago, Comment.id),])))
    unverified_comments = func.count(distinct(case([(Comment.verification==1, Comment.id),])))
    data['comments'], data['recent_comments'], data['unverified_comments'] = db.session\
        .query(comments, recent_comments, unverified_comments)\
        .all()[0]

    mod_query = db.session.query(User)\
        .filter(User.role_id==2)\
        .all()
    data['mod_ids'] = [x.id for x in mod_query]
    data['mods_count'] = len(data['mods'])
    return jsonify(data)

@api1.route('/mods/<int:id>/recs', methods=['GET'])
@api1.route('/mods/<int:id>/recs/page/<int:page>', methods=['GET'])
@admin_token_required
@auth_request(role=1)
def get_mod_rec_history(id, page=1):
    mod = User.query\
        .filter(User.role_id==2, User.id==id)\
        .first()
    if not mod:
        return message(404, 'This user is not a moderator')
    mod_recs = mod.rec_moderation\
        .order_by(desc(Rec_Moderation.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    return jsonify({x.id: x.to_json() for x in mod_recs.items})

@api1.route('/mods/<int:id>/comments', methods=['GET'])
@api1.route('/mods/<int:id>/comments/page/<int:page>', methods=['GET'])
@admin_token_required
@auth_request(role=1)
def get_mod_com_history(id, page=1):
    mod = User.query\
        .filter(User.role_id==2, User.id==id)\
        .first()
    if not mod:
        return message(404, 'This user is not a moderator')
    mod_coms = mod.com_moderation\
        .order_by(desc(Com_Moderation.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    return jsonify({x.id: x.to_json() for x in mod_coms.items})

@api1.route('/moderations/recs/<int:id>', methods=['GET'])
@admin_token_required
@auth_request(role=1)
def get_rec_mods(id):
    to_ret = Rec_Moderation.query\
        .get(int(id))
    if not to_ret:
        return message(404, 'This Rec Moderation does not exist')
    return jsonify(to_ret.to_json())

@api1.route('/moderations/recs/<int:id>', methods=['PUT'])
@admin_token_required
@auth_request(role=1)
def put_rec_mods(id):
    to_ret = Rec_Moderation.query\
        .get(int(id))
    if not to_ret:
        return message(404, 'This Rec Moderation does not exist')
    to_ret.action = not to_ret.action
    rec = to_ret.recommendation
    if to_ret.action is False:
        rec.verification = 0
        rec.made_private = True
        db.session.add(to_ret)
        db.session.add(rec)
        db.session.commit()
        return message(201, 'This rec has been made private')
    else:
        rec.verification = 2
        db.session.add(to_ret)
        db.session.add(rec)
        db.session.commit()
        return message(201, 'This rec has been verified')
    
@api1.route('/moderations/comments/<int:id>', methods=['GET'])
@admin_token_required
@auth_request(role=1)
def get_com_mods(id):
    to_ret = Com_Moderation.query\
        .get(int(id))
    if not to_ret:
        return message(404, 'This Comment Moderation does not exist')
    return jsonify(to_ret.to_json())

@api1.route('/moderations/comments/<int:id>', methods=['PUT'])
@admin_token_required
@auth_request(role=1)
def put_com_mods(id):
    to_ret = Com_Moderation.query\
        .get(int(id))
    if not to_ret:
        return message(404, 'This Comment Moderation does not exist')
    to_ret.action = not to_ret.action
    com = to_ret.comment
    if to_ret.action is False:
        com.verification = -1
        db.session.add(to_ret)
        db.session.add(com)
        db.session.commit()
        return message(201, 'This comment has been deleted')
    else:
        com.verification = 2
        db.session.add(to_ret)
        db.session.add(com)
        db.session.commit()
        return message(201, 'This comment has been verified')

@api1.route('/moderate/recs', methods=['GET'])
@api1.route('/moderate/recs/page/<int:page>', methods=['GET'])
@moderator_token_required
@auth_request(role=2)
def get_moderate_recs(page=1):
    recs = Recommendation.query\
        .filter_by(verification = 1)\
        .order_by(asc(Recommendation.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    to_ret = {x.id : x.to_json() for x in recs.items}
    return jsonify(to_ret)

@api1.route('/moderate/recs/<int:id>', methods=['POST'])
@moderator_token_required
@auth_request(role=2)
def moderate_recs(id):
    if not request.get_json(silent=True):
        return message(400, 'Must provide value for action')
    action = request.json.get('action')
    if action not in ['True', 'False']:
        return message(400, 'action must be true or false')
    rec = Recommendation.query\
        .filter_by(verification = 1, id=id)\
        .first()
    if not rec:
        return message(404, 'This rec cannot be modded. It is private or has been verified')
    if action == 'True':
        rec.verification = 2
    else:
        rec.verification = 0
        rec.made_private = True
    to_add = Rec_Moderation(user_id=g.current_user.id, recommendation_id=id, action=(rec.verification == 2))
    db.session.add(rec)
    db.session.add(to_add)
    db.session.commit()
    return message(201, 'Rec successfully moderated')

@api1.route('/moderate/comments', methods=['GET'])
@api1.route('/moderate/comments/page/<int:page>', methods=['GET'])
@moderator_token_required
@auth_request(role=2)
def get_moderate_comments(page=1):
    com = Comment.query\
        .filter_by(verification = 1)\
        .order_by(asc(Comment.timestamp))\
        .paginate(page, per_page=g.current_user.display, error_out=False)
    to_ret = {x.id : x.to_json() for x in com.items}
    return jsonify(to_ret)

@api1.route('/moderate/comments/<int:id>', methods=['POST'])
@moderator_token_required
@auth_request(role=2)
def moderate_comments(id):
    if not request.get_json(silent=True):
        return message(400, 'Must provide value for action')
    action = request.json.get('action')
    if action not in ['True', 'False']:
        return message(400, 'action must be true or false')
    comment = Comment.query\
        .filter_by(verification = 1, id=id)\
        .first()
    if not comment:
        return message(404, 'This comment cannot be modded. It has been deleted or has been verified')
    if action == 'True':
        comment.verification = 2
    else:
        comment.verification = -1
    to_add = Com_Moderation(user_id=g.current_user.id, comment_id=id, action=(comment.verification == 2))
    db.session.add(comment)
    db.session.add(to_add)
    db.session.commit()
    return message(201, 'Comment successfully moderated')