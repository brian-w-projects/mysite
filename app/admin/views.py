from flask import get_template_attribute, jsonify, render_template, request
from . import admin
from .. import db
from ..decorators import is_administrator
from ..models import Comment, Com_Moderation, Rec_Moderation, Recommendation, Relationship, User
from datetime import datetime, timedelta
from flask_login import current_user, login_required
from flask_moment import _moment
from sqlalchemy import case
from sqlalchemy.sql.expression import and_, desc, distinct, func
from ..tasks import prepare_comments

@admin.route('/-change-mod-comment-decision')
@login_required
@is_administrator
def change_mod_comment_decision():
    id = int(request.args.get('id'))
    comment = Comment.query\
        .get_or_404(int(id))
    mod = comment.com_moderation\
        .first_or_404()
    new_mod = Com_Moderation(action=not mod.action, user_id=current_user.id, comment_id=id )
    if mod.action:
        comment.verification = -1
    else:
        comment.verification = 2
    db.session.add(new_mod)
    db.session.delete(mod)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'verify': not mod.action})

@admin.route('/-change-mod-rec-decision')
@login_required
@is_administrator
def change_mod_decision():
    id = int(request.args.get('id'))
    rec = Recommendation.query\
        .get_or_404(int(id))
    mod = rec.rec_moderation\
        .first_or_404()
    new_mod = Rec_Moderation(action=not mod.action, user_id=current_user.id, recommendation_id=id)
    if mod.action:
        rec.verification = 0
        rec.made_private = True
    else:
        rec.verification = 2
        rec.made_private = False
    db.session.add(new_mod)
    db.session.delete(mod)
    db.session.add(rec)
    db.session.commit()
    return jsonify({'verify': not mod.action})

@admin.route('/-mod-history-com-ajax/<int:id>')
@login_required
@is_administrator
def mod_com_ajax(id):
    page = int(request.args.get('page'))
    mod = User.query\
        .filter(User.role_id.between(1,2), User.id==id)\
        .first_or_404()
    mod_coms = db.session.query(Comment, Relationship, Com_Moderation)\
        .outerjoin(Relationship, and_(
            Relationship.following==Comment.user_id,
            current_user.id == Relationship.follower
            )
        )\
        .filter(Com_Moderation.user_id == id, Com_Moderation.comment_id==Comment.id)\
        .order_by(desc(Com_Moderation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/admin/comment-action-macro.html', 'ajax')
    return jsonify({
        'last': mod_coms.pages in (0, mod_coms.page),
        'ajax_request': to_return(mod_coms, _moment, current_user)}) 

@admin.route('/-mod-history-rec-ajax/<int:id>')
@login_required
@is_administrator
def mod_rec_ajax(id):
    page = int(request.args.get('page'))
    mod_recs = db.session.query(Recommendation, Relationship, Rec_Moderation)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Rec_Moderation.user_id == id, Rec_Moderation.recommendation_id==Recommendation.id)\
        .order_by(desc(Rec_Moderation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/admin/rec-action-macro.html', 'ajax')
    process = [x[0].id for x in mod_recs.items]
    task = prepare_comments.apply_async([process, current_user.id])
    return jsonify({
        'last': mod_recs.pages in (0, mod_recs.page),
        'ajax_request': to_return(mod_recs, _moment, current_user),
        'id': task.id
    }) 

@admin.route('/mod-history/<int:id>')
@login_required
@is_administrator
def mod_history(id):
    mod = User.query\
        .filter(User.role_id.between(1,2), User.id==id)\
        .first_or_404()
    mod_recs = db.session.query(Recommendation, Relationship, Rec_Moderation)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Rec_Moderation.user_id == id, Rec_Moderation.recommendation_id==Recommendation.id)\
        .order_by(desc(Rec_Moderation.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    process = [x[0].id for x in mod_recs.items]
    task = prepare_comments.apply_async([process, current_user.id])
    mod_coms = db.session.query(Comment, Relationship, Com_Moderation)\
        .outerjoin(Relationship, and_(
            Relationship.following==Comment.user_id,
            current_user.id == Relationship.follower
            )
        )\
        .filter(Com_Moderation.user_id == id, Com_Moderation.comment_id==Comment.id)\
        .order_by(desc(Com_Moderation.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('admin/mod-history.html', mod=mod,
        mod_recs=mod_recs, mod_coms=mod_coms, id=task.id)
    
@admin.route('/splash')
@login_required
@is_administrator
def admin_splash():
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

    rec_mods = func.count(distinct(Rec_Moderation.id))
    recent_rec_mods = func.count(distinct(case([(Rec_Moderation.timestamp>week_ago, Rec_Moderation.id),])))
    com_mods = func.count(distinct(Com_Moderation.id))
    recent_com_mods = func.count(distinct(case([(Com_Moderation.timestamp>week_ago, Com_Moderation.id),])))
    data['mods'] = db.session.query(User, rec_mods, recent_rec_mods, com_mods, recent_com_mods)\
        .outerjoin(Rec_Moderation)\
        .outerjoin(Com_Moderation)\
        .filter(User.role_id == 2)\
        .group_by(User.username)\
        .all()
    return render_template('admin/splash.html', data=data)