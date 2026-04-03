from flask import abort, g
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from domain.core.constants import ROLE_ORDER
from utils.enums import UserRole
from domain import services


def role_required(required_role: UserRole = UserRole.client, inject_user=True):
    """Validate role and optionally store current_user in g."""

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            jwt_data = get_jwt()

            role_value = jwt_data.get("role")
            try:
                role = UserRole(role_value)
            except ValueError:
                abort(403, description="INVALID_ROLE")

            if ROLE_ORDER.get(role, 0) < ROLE_ORDER[required_role]:
                abort(403, description="INSUFFICIENT_ROLE")

            if inject_user:
                try:
                    user_id = int(get_jwt_identity())
                except (TypeError, ValueError):
                    abort(401, description="INVALID_IDENTITY")

                g.current_user = {
                    "id": user_id,
                    "role": role,
                }
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def require_active_user():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if user is None:
                abort(401, description="MISSING_AUTH_CONTEXT")

            if not services.user_exists_for_role(g.db, user["id"], user["role"]):
                abort(403, description="USER_NOT_FOUND")

            return fn(*args, **kwargs)

        return wrapper

    return decorator
