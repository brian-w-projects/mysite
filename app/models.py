from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer, JSONWebSignatureSerializer as Serializer
from flask import current_app, url_for, g
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime, timedelta
import random

random = random.SystemRandom()

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.BOOLEAN, default=False, index=True)
    users = db.relationship('Users', backref='role', lazy='dynamic')

    @staticmethod
    def generate_roles():
        role = Role(name='Administrator')
        db.session.add(role)
        role = Role(name='Moderator')
        db.session.add(role)
        role = Role(name='User', default=True)
        db.session.add(role)
        db.session.commit()

class API(db.Model):
    __tablename__ = 'apirequests'
    id = db.Column(db.INTEGER, primary_key=True)
    requester = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    endpoint = db.Column(db.String)
    role = db.Column(db.INTEGER, default=3)
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    
    @staticmethod
    def access_request(requester, endpoint, role=3):
        access = 0
        if role == 3 and not requester.is_administrator():
            fifteen_mins_ago = datetime.utcnow() - timedelta(minutes=15)
            access = API.query\
                .filter_by(requester = requester.id)\
                .filter_by(role = 3)\
                .filter(API.timestamp > fifteen_mins_ago)\
                .count()
        if access < 15:
            to_add = API(requester=requester.id, endpoint=endpoint, role=requester.role_id)
            db.session.add(to_add)
            db.session.commit()
            return True
        else:
            return False
        
        

class Followers(db.Model):
    __tablename__ = 'followers'
    id = db.Column(db.INTEGER, primary_key=True)
    follower = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    following = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    
    @staticmethod
    def generate_followers(count):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=Users.query.count()
        for i in range(count):
            u = Users.query.offset(randint(0, user_count-1)).first()
            v = Users.query.offset(randint(0, user_count-1)).first()
            u_time = datetime.strptime(str(u.member_since)[:10], '%Y-%m-%d')
            v_time = datetime.strptime(str(v.member_since)[:10], '%Y-%m-%d')
            if u_time < v_time:
                days_since = (datetime.utcnow() - v_time).days
            else:
                days_since = (datetime.utcnow() - u_time).days
            if days_since == 0:
                continue
            if u.id != v.id and not u.following.filter_by(following=v.id).first():
                f = Followers(follower=u.id, following=v.id,
                    timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since))
                db.session.add(f)
                db.session.commit()

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.INTEGER, primary_key=True)
    comment_by = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    posted_on = db.Column(db.INTEGER, db.ForeignKey('recs.id'))
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    verification = db.Column(db.INTEGER, default=1) 
    # verification = 0->private, 1->public and unchecked, 2->OKayed
    comment = db.Column(db.TEXT)
    moderation = db.relationship('ComModerations', backref='com', lazy='dynamic')
    
    @staticmethod
    def generate_comments(count):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=Users.query.count()
        rec_count=Recommendation.query.count()
        for i in range(count):
            u = Users.query.offset(randint(0, user_count - 1)).first()
            r = Recommendation.query.offset(randint(0, rec_count-1)).first()
            days_since = (datetime.utcnow() - datetime.strptime(str(r.timestamp)[:10], '%Y-%m-%d')).days
            c = Comments(comment_by=u.id,
                posted_on=r.id,
                timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                verification=1,
                comment=forgery_py.lorem_ipsum.sentences(randint(2,5)))
            db.session.add(c)
            db.session.commit()
            
    def to_json(self):
        json_rec = {
            'id': self.id,
            'author_id': self.comment_by,
            'author_username': self.comm.username,
            'posted_on': self.posted_on,
            'timestamp': self.timestamp,
            'comment': self.comment
        }
        return json_rec

class RecModerations(db.Model):
    __tablename__ = 'recmoderations'
    id = db.Column(db.INTEGER, primary_key=True)
    mod_by = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    mod_on = db.Column(db.INTEGER, db.ForeignKey('recs.id'))
    timestamp = db.Column(db.DATETIME, default=datetime.utcnow)
    action = db.Column(db.BOOLEAN)

    def to_json(self):
        json_rec = {
            'id': self.id,
            'timestamp': self.timestamp,
            'mod_by': self.mod_by,
            'mod_on': self.mod_on,
            'action': self.action,
            'text': self.rec.text,
            'title': self.rec.title,
            'author': self.rec.author_id
        }
        return json_rec

    @staticmethod
    def generate_recmods():
        from random import seed, randint
        import forgery_py
        
        seed()
        mods = Users.query.filter_by(role_id = 2)
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
                        to_add = RecModerations(mod_by=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            mod_on=rec_mod.id, action = True)
                        rec_mod.verification = 2
                        db.session.add(to_add)
                        db.session.add(rec_mod)
                        db.session.commit()
                    else:
                        to_add = RecModerations(mod_by=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            mod_on=rec_mod.id, action = False)
                        rec_mod.verification = 0
                        rec_mod.made_private = 1
                        db.session.add(to_add)
                        db.session.add(rec_mod)
                        db.session.commit()


class ComModerations(db.Model):
    __tablename__ = 'commoderations'
    id = db.Column(db.INTEGER, primary_key=True)
    mod_by = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    mod_on = db.Column(db.INTEGER, db.ForeignKey('comments.id'))
    timestamp = db.Column(db.DATETIME, default=datetime.utcnow)
    action = db.Column(db.BOOLEAN)
    
    def to_json(self):
        json_rec = {
            'id': self.id,
            'timestamp': self.timestamp,
            'mod_by': self.mod_by,
            'mod_on': self.mod_on,
            'action': self.action,
            'text': self.com.comment,
            'author': self.com.comment_by,
            'posted_on': self.com.posted_on
        }
        return json_rec
    
    @staticmethod
    def generate_commods():
        from random import seed, randint
        import forgery_py
        
        seed()
        mods = Users.query.filter_by(role_id = 2)
        com_count = Comments.query\
            .filter_by(verification=1)\
            .count()
        for mod in mods:
            for i in range(int(com_count / mods.count() * 0.9)):
                com_mod = Comments.query\
                    .filter_by(verification=1)\
                    .offset(randint(0, com_count-1))\
                    .first()
                if com_mod:
                    days_since = (datetime.utcnow() - datetime.strptime(str(com_mod.timestamp)[:10], '%Y-%m-%d')).days
                    if randint(0,1) == 0:
                        to_add = ComModerations(mod_by=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            mod_on=com_mod.id, action = True)
                        com_mod.verification = 2
                        db.session.add(to_add)
                        db.session.add(com_mod)
                        db.session.commit()
                    else:
                        to_add = ComModerations(mod_by=mod.id,
                            timestamp=forgery_py.date.date(True, min_delta=0, max_delta=days_since),
                            mod_on=com_mod.id, action = False)
                        com_mod.verification = 0
                        db.session.add(to_add)
                        db.session.add(com_mod)
                        db.session.commit()

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String(128))
    api = db.Column(db.String())
    updates = db.Column(db.BOOLEAN, default=True)
    confirmed = db.Column(db.BOOLEAN, default=False)
    role_id = db.Column(db.INTEGER, db.ForeignKey('roles.id'))
    display = db.Column(db.INTEGER, default=10)
    about_me = db.Column(db.TEXT)
    member_since = db.Column(db.DATETIME, default=datetime.utcnow)
    last_login = db.Column(db.DATETIME, default=datetime.utcnow)
    invalid_logins = db.Column(db.INTEGER, default=0)
    rec_mods = db.relationship('RecModerations', backref='user', lazy='dynamic')
    com_mods = db.relationship('ComModerations', backref='user', lazy='dynamic')
    posts = db.relationship('Recommendation', backref='author', lazy='dynamic')
    following = db.relationship('Followers', backref='user', 
        foreign_keys=[Followers.follower], lazy='dynamic')
    followed_by = db.relationship('Followers', backref='who', lazy='dynamic',
        foreign_keys=[Followers.following])
    commented_on = db.relationship('Comments', foreign_keys=[Comments.comment_by],
        backref=db.backref('comm', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')

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
        return Users.get_random_string(10, chars)

    def generate_auth_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        self.api = s.dumps({'id': self.id})
        db.session.add(self)
        db.session.commit()
        return s.dumps({'id': self.id})
    
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        user = Users.query.get(data['id'])
        if user.api == token:
            return user
        else:
            return None

    def to_json(self):
        json_rec = {
            'username': self.username,
            'confirmed': self.confirmed,
            'display': self.display,
            'about_me': self.about_me,
            'member_since': self.member_since,
            'recs': self.posts.filter_by(verification=2).count(),
            'following_count' : self.following.count(),
            'followed_by_count': self.followed_by.count(),
            'comments': self.commented_on.filter_by(verification=2).count(),
            'id': self.id
        }
        if g.current_user.is_administrator():
            json_rec['email'] = self.email
            json_rec['role_id'] = self.role_id
            json_rec['last_login'] = self.last_login
            if self.is_moderator():
                json_rec['rec_mods'] = self.rec_mods.count()
                json_rec['com_mods'] = self.com_mods.count()
        return json_rec

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
            
            u = Users(username=forgery_py.internet.user_name(True),
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
    return Users.query.get(int(user_id))


class Recommendation(db.Model):
    __tablename__ = 'recs'
    id = db.Column(db.INTEGER, primary_key=True)
    title = db.Column(db.String(64))
    timestamp = db.Column(db.DATETIME, index=True, default=datetime.utcnow)
    author_id = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    text = db.Column(db.TEXT)
    new_comment = db.Column(db.BOOLEAN, default=False)
    verification = db.Column(db.INTEGER) 
    # verification = -1-> deleted, 0->private, 1->public and unchecked, 2->OKayed
    made_private = db.Column(db.BOOLEAN, default=False)
    moderation = db.relationship('RecModerations', backref='rec', lazy='dynamic')
    comments = db.relationship('Comments', foreign_keys=[Comments.posted_on],
        backref=db.backref('posted', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    
    def to_json(self):
        json_rec = {
            'text': self.text,
            'title': self.title,
            'author': self.author.username,
            'author_id': self.author_id,
            'timestamp': self.timestamp,
            'comment_count': self.comments.filter(Comments.verification != 0).count(),
            'id': self.id,
            'private': self.verification == 0
        }
        return json_rec
    
    def to_json_comments(self):
        json_rec = {com.id : com.to_json() for com in self.comments if com.verification != 0}
        return json_rec
    
    @staticmethod
    def generate_recs(count):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=Users.query.count()
        for i in range(count):
            u = Users.query.offset(randint(0, user_count - 1)).first()
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
                author=u,
                text=forgery_py.lorem_ipsum.sentences(randint(2,8)),
                verification=verified)
            db.session.add(r)
            db.session.commit()