from . import celery
from . import db
from .models import Comment, Relationship, User, Recommendation
from sqlalchemy.sql.expression import and_, desc
from . import mail


@celery.task(bind=True)
def prepare_comments(self, process, id):
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

@celery.task
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)