from flask import get_template_attribute, jsonify, render_template, request
from . import mod
from .. import db
from ..decorators import is_moderator
from ..models import Comment, Com_Moderation, Rec_Moderation, Recommendation, Relationship
from flask_login import login_required, current_user
from flask_moment import _moment
from sqlalchemy.sql.expression import and_, asc
from ..tasks import prepare_comments

@mod.route('/-moderate-comments')
@login_required
@is_moderator
def moderate_com():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = Com_Moderation(user_id=current_user.id, comment_id=id, action=verify)
    db.session.add(new_mod)
    com = Comment.query\
        .filter_by(id=id)\
        .first_or_404()
    if verify == 'true':
        com.verification = 2
    else:
        com.verificition = -1
    db.session.add(com)
    db.session.commit()
    return jsonify({'verify': verify == 'true'})

@mod.route('/verify-comments')
@login_required
@is_moderator
def verify_comments():
    page = int(request.args.get('page', default=1))
    display_comments = db.session.query(Comment, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following==Comment.user_id,
            current_user.id == Relationship.follower
            )
        )\
        .filter(Comment.verification==1)\
        .order_by(asc(Comment.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    if request.is_xhr: #ajax
        to_return = get_template_attribute('macros/moderator/mod-comment-macro.html', 'ajax')
        return jsonify({
            'last': display_comments.pages in (0, display_comments.page),
            'ajax_request': to_return(display_comments, _moment, current_user)}) 
    return render_template('mod/verify-comments.html', d_c=display_comments)

@mod.route('/-moderate-recs')
@login_required
@is_moderator
def moderate_recs():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = Rec_Moderation(user_id=current_user.id, recommendation_id=id, action=verify)
    db.session.add(new_mod)
    rec = Recommendation.query\
            .filter_by(id=id)\
            .first_or_404()
    if verify == 'true':
        rec.verification = 2
    else:
        rec.verification = 0
        rec.made_private = True
    db.session.add(rec)
    db.session.commit()
    return jsonify({'verify': verify=='true'})

@mod.route('/verify-recs')
@login_required
@is_moderator
def verify_recs():
    page = int(request.args.get('page', default=1))
    display_recs = db.session.query(Recommendation, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Recommendation.verification==1)\
        .order_by(asc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    process = [x[0].id for x in display_recs.items]
    task = prepare_comments.apply_async([process, current_user.id])
    if request.is_xhr: #ajax
        to_return = get_template_attribute('macros/moderator/mod-rec-macro.html', 'ajax')        
        return jsonify({
            'last': display_recs.pages in (0, display_recs.page),
            'ajax_request': to_return(display_recs, _moment, current_user),
            'id': task.id
        })
    return render_template('mod/verify-recs.html', display=display_recs, id=task.id)