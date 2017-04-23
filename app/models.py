from flask import current_app, g, url_for
from . import db
from . import login_manager
from datetime import datetime, timedelta
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer, JSONWebSignatureSerializer as Serializer
from random import SystemRandom
from sqlalchemy.orm import backref
from sqlalchemy.sql.expression import desc
from werkzeug.security import check_password_hash, generate_password_hash


random = SystemRandom()

class API_Request(db.Model):
    __tablename__ = 'api_request'
    id = db.Column(db.INTEGER, primary_key=True)
    endpoint = db.Column(db.String)
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    
    user = db.relationship('User', backref=backref('api_request', lazy='dynamic'))
    
    @staticmethod
    def access_request(requester, endpoint, role=3):
        access = 0
        if role == 3 and not requester.is_administrator():
            fifteen_mins_ago = datetime.utcnow() - timedelta(minutes=15)
            access = API_Request.query\
                .filter(API_Request.user_id==requester.id, API_Request.timestamp>fifteen_mins_ago)\
                .count()
        if access < 15:
            to_add = API_Request(endpoint=endpoint, user_id=requester.id)
            db.session.add(to_add)
            db.session.commit()
            return True
        else:
            return False


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.INTEGER, primary_key=True)
    recommendation_id = db.Column(db.INTEGER, db.ForeignKey('recommendation.id'))
    text = db.Column(db.TEXT)
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    verification = db.Column(db.INTEGER, default=1) 
    # verification = 0->private, 1->public and unchecked, 2->OKayed
    
    recommendation = db.relationship('Recommendation', backref=backref('comment', lazy='dynamic'))
    user = db.relationship('User', backref=backref('comment', lazy='dynamic'))

    @staticmethod
    def generate_comments(count):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=User.query.count()
        rec_count=Recommendation.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            r = Recommendation.query.offset(randint(0, rec_count-1)).first()
            days_since = (datetime.utcnow() - datetime.strptime(str(r.timestamp)[:10], '%Y-%m-%d')).days
            c = Comment(user_id=u.id, recommendation_id=r.id,
                timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                verification=1,
                text=forgery_py.lorem_ipsum.sentences(randint(2,5)))
            db.session.add(c)
            db.session.commit()
            
    def to_json(self):
        return {
            'id': self.id,
            'author_id': self.user_id,
            'author_username': self.user.username,
            'posted_on': self.recommendation_id,
            'timestamp': self.timestamp,
            'text': self.text
        }


class Com_Moderation(db.Model):
    __tablename__ = 'com_moderation'
    id = db.Column(db.INTEGER, primary_key=True)
    action = db.Column(db.BOOLEAN)
    comment_id = db.Column(db.INTEGER, db.ForeignKey('comment.id'))
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))

    comment = db.relationship('Comment', backref='comment')
    user = db.relationship('User', backref=backref('com_moderation', lazy='dynamic'))
    
    @staticmethod
    def generate_commods():
        from random import seed, randint
        import forgery_py
        
        seed()
        mods = User.query.filter_by(role_id = 2)
        com_count = Comment.query\
            .filter_by(verification=1)\
            .count()
        for mod in mods:
            for i in range(int(com_count / mods.count() * 0.9)):
                com_mod = Comment.query\
                    .filter_by(verification=1)\
                    .offset(randint(0, com_count-1))\
                    .first()
                if com_mod:
                    days_since = (datetime.utcnow() - datetime.strptime(str(com_mod.timestamp)[:10], '%Y-%m-%d')).days
                    if randint(0,1) == 0:
                        to_add = Com_Moderation(user_id=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            comment_id=com_mod.id, action = True)
                        com_mod.verification = 2
                        db.session.add(to_add)
                        db.session.add(com_mod)
                        db.session.commit()
                    else:
                        to_add = Com_Moderation(user_id=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            comment_id=com_mod.id, action = False)
                        com_mod.verification = 0
                        db.session.add(to_add)
                        db.session.add(com_mod)
                        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'action': self.action,
            'author': self.user.username,
            'author_id': self.user_id,
            'comment_id': self.comment_id,
            'posted_on': self.comment.recommendation_id,
            'text': self.comment.text,
            'timestamp': self.timestamp,
        }


class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    id = db.Column(db.INTEGER, primary_key=True)
    made_private = db.Column(db.BOOLEAN, default=False)
    new_comment = db.Column(db.BOOLEAN, default=False)
    text = db.Column(db.TEXT)
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    title = db.Column(db.String(64))
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    verification = db.Column(db.INTEGER) 
    # verification = -1-> deleted, 0->private, 1->public and unchecked, 2->OKayed

    user = db.relationship('User', backref=backref('recommendation', lazy='dynamic'))
    
    def prepare_comments(self):
        prep_query = self.comment\
            .filter(Comment.verification > 0)\
            .order_by(desc(Comment.timestamp))
        d_c = prep_query\
            .paginate(1, per_page=5, error_out=False)
        count = prep_query.count()
        return (d_c, count)
    
    def to_json(self):
        return {
            'id': self.id,
            'author': self.user.username,
            'author_id': self.user_id,
            'comment_count': self.comment.filter(Comment.verification>0).count(),
            'private': self.verification == 0,
            'text': self.text,
            'timestamp': self.timestamp,
            'title': self.title
        }
    
    # put in comments?
    def to_json_comments(self):
        json_rec = {com.id : com.to_json() for com in self.comment if com.verification != 0}
        return json_rec
    
    @staticmethod
    def generate_recs(count):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            days_since = (datetime.utcnow() - datetime.strptime(str(u.member_since)[:10], '%Y-%m-%d')).days
            if days_since == 0:
                continue
            if randint(0,10)<8:
                verified = 1
            elif randint(0,1) == 0:
                verified = 0
            else:
                verified = -1
            r = Recommendation(title=forgery_py.lorem_ipsum.sentence(),
                timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                user=u,
                text=forgery_py.lorem_ipsum.sentences(randint(2,8)),
                verification=verified)
            db.session.add(r)
            db.session.commit()


class Rec_Moderation(db.Model):
    __tablename__ = 'rec_moderation'
    id = db.Column(db.INTEGER, primary_key=True)
    action = db.Column(db.BOOLEAN)
    recommendation_id = db.Column(db.INTEGER, db.ForeignKey('recommendation.id'))
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))

    user = db.relationship('User', backref=backref('rec_moderation', lazy='dynamic'))
    recommendation = db.relationship('Recommendation', backref='rec_moderation')

    @staticmethod
    def generate_recmods():
        from random import seed, randint
        import forgery_py
        
        seed()
        mods = User.query.filter_by(role_id = 2)
        rec_count = Recommendation.query.filter_by(verification=1).count()
        for mod in mods:
            for i in range(int(rec_count / mods.count() * 0.9)):
                rec_mod = Recommendation.query\
                    .filter_by(verification=1)\
                    .offset(randint(0, rec_count-1))\
                    .first()
                if rec_mod:
                    days_since = (datetime.utcnow() - datetime.strptime(str(rec_mod.timestamp)[:10], '%Y-%m-%d')).days
                    if randint(0,1) == 0:
                        to_add = Rec_Moderation(user_id=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            recommendation_id=rec_mod.id, action = True)
                        rec_mod.verification = 2
                        db.session.add(to_add)
                        db.session.add(rec_mod)
                        db.session.commit()
                    else:
                        to_add = Rec_Moderation(user_id=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            recommendation_id=rec_mod.id, action = False)
                        rec_mod.verification = 0
                        rec_mod.made_private = 1
                        db.session.add(to_add)
                        db.session.add(rec_mod)
                        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'action': self.action,
            'author': self.recommention.author_id,
            'recommendation_id': self.recommendation_id,
            'text': self.recommendation.text,
            'timestamp': self.timestamp,
            'title': self.recommention.title,
            'user_id': self.user_id
        }
        
        
class Relationship(db.Model):
    __tablename__ = 'relationship'
    id = db.Column(db.INTEGER, primary_key=True)
    follower = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    following = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    
    user_follower = db.relationship('User', backref=backref('following', lazy='dynamic'),
        foreign_keys=[follower])
    user_following = db.relationship('User', backref=backref('follower', lazy='dynamic'),
        foreign_keys=[following])
    
    @staticmethod
    def generate_followers(count):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count-1)).first()
            v = User.query.offset(randint(0, user_count-1)).first()
            u_time = datetime.strptime(str(u.member_since)[:10], '%Y-%m-%d')
            v_time = datetime.strptime(str(v.member_since)[:10], '%Y-%m-%d')
            if u_time < v_time:
                days_since = (datetime.utcnow() - v_time).days
            else:
                days_since = (datetime.utcnow() - u_time).days
            if days_since == 0:
                continue
            if u.id != v.id and not u.following.filter_by(following=v.id).first():
                f = Relationship(follower=u.id, following=v.id,
                    timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since))
                db.session.add(f)
                db.session.commit()


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.INTEGER, primary_key=True)
    default = db.Column(db.BOOLEAN, default=False, index=True)
    name = db.Column(db.String(64), unique=True)

    @staticmethod
    def generate_roles():
        role = Role(name='Administrator')
        db.session.add(role)
        role = Role(name='Moderator')
        db.session.add(role)
        role = Role(name='User', default=True)
        db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.INTEGER, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    email = db.Column(db.String, unique=True, index=True)
    about_me = db.Column(db.TEXT)
    api = db.Column(db.String())
    confirmed = db.Column(db.BOOLEAN, default=False)
    display = db.Column(db.INTEGER, default=10)
    invalid_logins = db.Column(db.INTEGER, default=0)
    last_login = db.Column(db.DATETIME, default=datetime.utcnow)
    member_since = db.Column(db.DATETIME, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.INTEGER, db.ForeignKey('role.id'))
    updates = db.Column(db.BOOLEAN, default=True)
    
    role = db.relationship('Role', backref=backref('user', lazy='dynamic'))

    @property
    def password(self):
        raise AttributeError('password is hashed')

    @password.setter
    def password(self, p):
        self.password_hash = generate_password_hash(p)

    def verify_password(self, p):
        return check_password_hash(self.password_hash, p)

    def generate_confirmation_token(self, expiration=3600):
        s = TimedSerializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = TimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def is_moderator(self):
        return self.role_id == 2 or self.role_id == 1

    def is_administrator(self):
        return self.role_id == 1
        
    @staticmethod
    def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        return ''.join(random.choice(allowed_chars) for i in range(length))
 
    @staticmethod
    def get_secret_key():
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return User.get_random_string(10, chars)

    def generate_auth_token(self):
        s = TimedSerializer(current_app.config['SECRET_KEY'])
        self.api = s.dumps({'id': self.id})
        db.session.add(self)
        db.session.commit()
        return s.dumps({'id': self.id})
    
    @staticmethod
    def verify_auth_token(token):
        s = TimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        user = User.query.get(data['id'])
        if user.api == token:
            return user
        else:
            return None

    def to_json(self):
        json_rec = {
            'id': self.id,
            'about_me': self.about_me,
            'comments': self.comment.filter(Comment.verification>0).count(),
            'confirmed': self.confirmed,
            'display': self.display,
            'followed_by_count': self.followed_by.count(),
            'following_count' : self.following.count(),
            'member_since': self.member_since,
            'recs': self.recommendation.filter(Recommendation.verification>0).count(),
            'username': self.username
        }
        if g.current_user.is_administrator():
            json_rec['email'] = self.email
            json_rec['role_id'] = self.role_id
            json_rec['last_login'] = self.last_login
            if self.is_moderator():
                json_rec['rec_mods'] = self.rec_mods.count()
                json_rec['com_mods'] = self.com_mods.count()
        return json_rec

    # move to relationship?
    def to_json_following(self):
        json_rec = {}
        json_rec['count'] = self.following.count()
        json_rec['following'] = {following.id : following.timestamp for following in self.following}
        return json_rec
    
    def to_json_followed(self):
        json_rec = {}
        json_rec['count'] = self.followed_by.count()
        json_rec['followed_by'] = {followed_by.id : followed_by.timestamp for followed_by in self.followed_by}
        return json_rec

    @staticmethod
    def generate_users(count, preload = None):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py
        
        seed()
        for custom in preload:
            custom.member_since=forgery_py.date.date(True, min_delta=0, max_delta=365)
            db.session.add(custom)
            db.session.commit()
        
        for i in range(count):
            if randint(0,100) == 10:
                role = 2
            else:
                role = 3
            
            u = User(username=forgery_py.internet.user_name(True),
                email=forgery_py.internet.email_address(),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                role_id = role,
                about_me=forgery_py.lorem_ipsum.sentences(randint(3,5)),
                member_since=forgery_py.date.date(True, min_delta=0, max_delta=365),
                last_login=forgery_py.date.date(True, min_delta=0, max_delta=100))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    id = -1
    display = 10
    
    def is_moderator(self):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))