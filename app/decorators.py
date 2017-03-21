from functools import wraps
from flask import abort, g, request, jsonify
from flask_login import current_user
from .models import Users
from .import db

def message(code, message):
    response = jsonify({'Code': code, 'message': message})
    response.status_code = code
    return response

def auth_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.authorization:
            return message(401, 'Must send username and password for authentication')
        username = request.authorization['username']
        password = request.authorization['password']
        user = Users.query\
            .filter_by(username=username)\
            .first()
        if not user or not user.verify_password(password):
            user.invalid_logins += 1
            db.session.add(user)
            db.session.commit()
            return message(403, 'Invalid username/password')
        if user.invalid_logins >= 5:
            return message(403, 'This account has been locked')
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
            return message(401, 'Must send token for authentication')
        token = request.authorization['username']
        check = Users.verify_auth_token(token)
        if check is None:
            return message(401, 'Invalid token')
        g.current_user = check
        return f(*args, **kwargs)
    return decorated_function

def moderator_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.authorization:
            return message(401, 'Must send token for authentication')
        token = request.authorization['username']
        check = Users.verify_auth_token(token)
        if check is None:
            return message(401, 'Invalid token')
        if not check.is_moderator():
            return message(403, 'You do not have permission to view this page')
        g.current_user = check
        return f(*args, **kwargs)
    return decorated_function

def admin_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.authorization:
            return message(401, 'Must send token for authentication')
        token = request.authorization['username']
        check = Users.verify_auth_token(token)
        if check is None:
            return message(401, 'Invalid token')
        if not check.is_administrator():
            return message(403, 'You do not have permission to view this page')
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