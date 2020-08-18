from functools import wraps
from flask import abort
from flask_login import current_user
from demo.models import Permission


def permission_required(permission):
    """Decorator to check if current_user has permission
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def moderate_required(f):
    return permission_required(Permission.MODERATE)(f)
