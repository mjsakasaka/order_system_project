from typing import Callable, Iterable, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.user import User
from ..services.auth_service import get_user_by_token
from ..core.errors import AppError, ErrorCode

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> User:
    """
    Read token from 'Authorization: Bearer <token>'
    Then load user from DB.
    """
    if credentials is None or not credentials.credentials:
        raise AppError(
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
            message="Missing bearer token",
            http_status=401,
        )
    token = credentials.credentials
    return get_user_by_token(db, token)

def require_roles(*allowed_roles: str) -> Callable:
    """
    Usage:
        @router.get(...)
        def api(..., user=Depends(require_roles("ADMIN","CS"))):
            ...
    """
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise AppError(
                error_code=ErrorCode.AUTH_FORBIDDEN,
                message=f"Role '{user.role}' is not allowed",
                http_status=403,
                details={"allowed_roles": list(allowed_roles), "role": user.role},
            )
        return user
    return _dep
