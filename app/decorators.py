from functools import wraps
from flask import abort, g, request
from flask_login import current_user
from .models import Users
from .import db

def auth_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.authorization:
            abort(403)
        username = request.authorization['username']
        password = request.authorization['password']
        user = Users.query\
            .filter_by(username=username)\
            .first_or_404()
        check = user.verify_password(password)
        if check is False:
            user.invalid_logins += 1
            db.session.add(user)
            db.session.commit()
            abort(401)
        user.invalid_logins = 0
        db.session.add(user)
        db.session.commit()
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def auth_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.authorization:
            abort(403)
        token = request.authorization['username']
        check = Users.verify_auth_token(token)
        if check is None:
            abort(401)
        g.current_user = check
        return f(*args, **kwargs)
    return decorated_function

def admin_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.authorization:
            abort(403)
        token = request.authorization['username']
        check = Users.verify_auth_token(token)
        if check is None or not check.is_administrator():
            abort(403)
        g.current_user = check
        return f(*args, **kwargs)
    return decorated_function

def is_moderator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_moderator() or current_user.is_administrator()):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def is_administrator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_administrator():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function