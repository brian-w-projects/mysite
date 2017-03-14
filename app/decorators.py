from functools import wraps
from flask import abort
from flask_login import current_user
# from .models import Permission

# def permission_required(permission):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if not current_user.can(permission):
#                 abort(403)
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

def is_moderator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_moderator() or not current_user.is_administrator():
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