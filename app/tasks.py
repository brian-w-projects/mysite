from . import celery
from . import db
from .models import Comment, Relationship, User, Recommendation
from sqlalchemy.sql.expression import and_, desc, or_, func
from . import mail
from flask import current_app
from flask_mail import Message
import sendgrid
import os
from sendgrid.helpers.mail import *


@celery.task(bind=True)
def prepare_comments(self, process, id):
    self.update_state(state='PROGRESS')
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
        
@celery.task(bind=True)
def updates(self, msg):
    self.update_state(state='PROGRESS')
    to_send = User.query\
        .filter_by(updates=True)\
        .all()
    for user in to_send:
        my_list = [max(x.title.split(), key=len) for x in user.recommendation\
            .order_by(desc(Recommendation.timestamp))\
            .limit(10)]
        display_recs = Recommendation.query\
            .filter(Recommendation.verification>0, Recommendation.user_id!=user.id)\
            .filter(or_(*[Recommendation.title.contains(list_ele) for list_ele in my_list]))\
            .order_by(desc(Recommendation.timestamp))\
            .limit(50)\
            .from_self()\
            .order_by(func.random())\
            .limit(5)
        msg = Message('Weekly Update', sender=current_app._get_current_object().config['MAIL_USERNAME'], recipients=[user.email])
        msg.body = 'Hey ' + user.username + '\n Check out some of these recent recs:' \
            + 'Title \n\n from, \n The Recommend Me Teams'
        send_async_email(current_app._get_current_object(), msg)