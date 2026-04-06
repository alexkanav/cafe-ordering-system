from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from utils.enums import UserRole
from fastapi_app.auth.jwt import decode_access_token
from fastapi_app.dependencies.db import get_db
from domain.schemas import CurrentUserSchema
from domain.core.errors import NotFoundError, DomainValidationError, NOT_AUTHENTICATED, INSUFFICIENT_ROLE, \
    USER_NOT_FOUND
from domain.core.constants import ROLE_ORDER
from domain.services.user import user_exists_for_role


def get_current_user(request: Request) -> CurrentUserSchema:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NOT_AUTHENTICATED
        )
    try:
        payload = decode_access_token(token)

    except (NotFoundError, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    return CurrentUserSchema(
        id=int(payload.sub),
        role=UserRole(payload.role),
    )


def require_min_role(min_role: UserRole):
    def dependency(
            current_user: CurrentUserSchema = Depends(get_current_user),
    ) -> CurrentUserSchema:
        if ROLE_ORDER[current_user.role] < ROLE_ORDER[min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=INSUFFICIENT_ROLE,
            )
        return current_user

    return dependency


def require_valid_user(role: UserRole):
    def dependency(
            current_user: CurrentUserSchema = Depends(require_min_role(role)),
            db: Session = Depends(get_db),
    ) -> CurrentUserSchema:
        if not user_exists_for_role(db, current_user.id, current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=USER_NOT_FOUND,
            )
        return current_user

    return dependency
