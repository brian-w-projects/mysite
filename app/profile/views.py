from flask import flash, get_template_attribute, jsonify, redirect, render_template, request, url_for
from . import profile
from .. import db
from ..models import  Comment, Recommendation, Relationship, User
from flask_login import current_user, login_required
from flask_moment import _moment
from sqlalchemy import case
from sqlalchemy.sql.expression import and_, desc, or_

@profile.route('/-profile-com/<int:id>')
def profile_com_ajax(id):
    page = int(request.args.get('page'))
    display_comments = db.session.query(Comment, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following==Comment.user_id,
            current_user.id == Relationship.follower
            )
        )\
        .filter(Comment.verification>0, 
            Comment.user_id==id)\
        .order_by(desc(Comment.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/comment-macro.html', 'ajax')
    return jsonify({
        'last': display_comments.pages in (0, display_comments.page),
        'ajax_request': to_return(display_comments, _moment, current_user, 
            link=url_for('profile.user_profile', username=User.query.get(int(id))))}) 

@profile.route('/-profile-rec/<int:id>')
def profile_ajax(id):
    page = int(request.args.get('page'))
    ver_case = case([(db.true() if current_user.id==id else db.false(), 0),], else_=1)
    display_recs = db.session.query(Recommendation, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Recommendation.user_id==id, Recommendation.verification>=ver_case)\
        .order_by(desc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out = False)
    to_return = get_template_attribute('macros/rec-macro.html', 'ajax')
    return jsonify({
        'last': display_recs.pages in (0, display_recs.pages),
        'ajax_request': to_return(display_recs, _moment, current_user, 
            link=url_for('profile.user_profile', username=User.query.get(int(id))))}) 

@profile.route('/<string:username>')
@profile.route('/')
def user_profile(username = None):
    if username is None and current_user.is_authenticated:
        return redirect(url_for('profile.user_profile', username=current_user.username))
    user = User.query\
        .filter_by(username=username)\
        .first_or_404()
    com_count = 0
    rec_count = 0
    if current_user.is_moderator() and current_user == user:
        com_count = Comment.query\
            .filter_by(verification=1)\
            .count()
        rec_count = Recommendation.query\
            .filter_by(verification=1)\
            .count()
    ver_case = case([(db.true() if current_user==user else db.false(), 0),], else_=1)
    display_recs = db.session.query(Recommendation, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following == Recommendation.user_id,
            Relationship.follower == current_user.id)
        )\
        .filter(Recommendation.verification>=ver_case, Recommendation.user==user)\
        .order_by(desc(Recommendation.timestamp))
    display_comments = db.session.query(Comment, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following==Comment.user_id,
            current_user.id == Relationship.follower
            )
        )\
        .filter(Comment.verification>0, 
            Comment.user_id==user.id)\
        .order_by(desc(Comment.timestamp))
    if current_user.id == id:
        for rec in display_recs:
            if rec[0].made_private:
                title = (rec[0].title + '...') if len(rec[0].title) > 10 else rec[0].title
                flash("Rec '" + title + "' has been made private due to it's content.")
                rec[0].made_private = False
                db.session.add(rec[0])
            db.session.commit()
    display_recs = display_recs\
        .paginate(1, per_page=current_user.display, error_out=False)
    display_comments = display_comments\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('profile/profile.html', user=user, display=display_recs, 
        d_c=display_comments, com_count = com_count, rec_count=rec_count)