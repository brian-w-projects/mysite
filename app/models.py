from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
import random
random = random.SystemRandom()

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('Users', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_by_user = db.Column(db.String, db.ForeignKey('users.username'))
    posted_on = db.Column(db.Integer, db.ForeignKey('recs.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comment = db.Column(db.Text)
    
    @staticmethod
    def generate_comments(count=1000):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=Users.query.count()
        rec_count=Recommendation.query.count()
        for i in range(count):
            u = Users.query.offset(randint(0, user_count - 1)).first()
            r = Recommendation.query.offset(randint(0, rec_count-1)).first()
            c = Comments(comment_by=u.id,
                comment_by_user=u.username,
                posted_on=r.id,
                timestamp=forgery_py.date.date(True),
                comment=forgery_py.lorem_ipsum.sentences(randint(2,8)))
            r.likes += 1
            db.session.add(r)
            db.session.add(c)
            db.session.commit()

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String(128))
    updates = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.INTEGER, db.ForeignKey('roles.id'))
    display = db.Column(db.Integer, default=10)
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DATETIME(), default=datetime.utcnow)
    last_login = db.Column(db.DATETIME(), default=datetime.utcnow)
    invalid_logins = db.Column(db.Integer, default=0)
    posts = db.relationship('Recommendation', backref='author', lazy='dynamic')
    commented_on = db.relationship('Comments', foreign_keys=[Comments.comment_by],
        backref=db.backref('comm', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')


    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is hashed')

    @password.setter
    def password(self, p):
        self.password_hash = generate_password_hash(p)

    def verify_password(self, p):
        return check_password_hash(self.password_hash, p)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
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

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
        
    @staticmethod
    def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        return ''.join(random.choice(allowed_chars) for i in range(length))
 
    @staticmethod
    def get_secret_key():
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return Users.get_random_string(10, chars)

    @staticmethod
    def generate_users(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py
        
        seed()
        for i in range(count):
            u = Users(username=forgery_py.internet.user_name(True),
                email=forgery_py.internet.email_address(),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                about_me=forgery_py.lorem_ipsum.sentences(randint(3,5)),
                member_since=forgery_py.date.date(True),
                last_login=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Recommendation(db.Model):
    __tablename__ = 'recs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    public = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text)
    new_comment = db.Column(db.Boolean, default=False)
    verification = db.Column(db.Integer) 
    # verificaiton = 0->private, 1->public and unchecked, 2->OKayed
    comments = db.relationship('Comments', foreign_keys=[Comments.posted_on],
        backref=db.backref('posted', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    
    @staticmethod
    def generate_recs(count=1000):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count=Users.query.count()
        for i in range(count):
            u = Users.query.offset(randint(0, user_count - 1)).first()
            pub = randint(0,10)<8
            if pub:
                ver = 1
            else:
                ver = 0
            r = Recommendation(title=forgery_py.lorem_ipsum.sentence(),
                public=pub,
                timestamp=forgery_py.date.date(True),
                author=u,
                text=forgery_py.lorem_ipsum.sentences(randint(2,8)),
                verification=ver)
            
            db.session.add(r)
            db.session.commit()