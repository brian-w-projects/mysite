from . import celery
from .models import Comment, Relationship, User, Recommendation
from . import db
from sqlalchemy.sql.expression import desc, and_
from flask_login import AnonymousUserMixin, UserMixin, current_user
from flask_moment import _moment
from flask import jsonify, get_template_attribute, url_for

@celery.task(bind=True)
def test(self, process, id):
    self.update_state(state='PROGRESS', meta={'a': 1})
    to_ret = {}
    
    for x in process:
        prep_query = db.session.query(Comment, Relationship)\
            .outerjoin(Relationship, and_(
                Relationship.following==Comment.user_id,
                id == Relationship.follower
                )
            )\
            .filter(Comment.verification > 0,
                Comment.recommendation_id==x)\
            .order_by(desc(Comment.timestamp))\
            .limit(5)
        to_ret[x] = [(com.id, rel != None) for com, rel in prep_query]
    return to_ret


@celery.task(bind=True)
def testb(self):
    self.update_state(state='PROGRESS')
    d_c = db.session.query(Comment, Relationship)\
        .outerjoin(Relationship, and_(
            Relationship.following==Comment.user_id,
            current_user.id == Relationship.follower
            )
        )\
        .filter(Comment.verification > 0,
            Comment.recommendation_id==self.id)\
        .order_by(desc(Comment.timestamp))\
        .paginate(1, per_page=5, error_out=False)
    to_return = get_template_attribute('macros/comment-macro.html', 'ajax')
    return jsonify({'status': 'FINISHED',
        'ajax_request': to_return(d_c, _moment, current_user)}) 