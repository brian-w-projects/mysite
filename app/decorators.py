from functools import wraps
from flask import abort
from flask_login import current_user

def auth_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        check = current_user.verify_auth_token(kwargs['token'])
        if check is None or not check.id == current_user.id:
            abort(403)
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