from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.user import User
from ..core.security import verify_password
from ..core.errors import AppError, ErrorCode

def login(db: Session, username: str, password: str) -> User:
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise AppError(
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
            message="Invalid username or password",
            http_status=401,
        )
    return user

def issue_token(user: User) -> str:
    # 最小可用：之后换 JWT 也不会影响业务层测试思路
    return f"token:{user.id}"


from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models.user import User
from ..core.errors import AppError, ErrorCode

def parse_token(token: str) -> int:
    """
    token format: 'token:<user_id>'
    """
    if not token or not token.startswith("token:"):
        raise AppError(
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
            message="Invalid token format",
            http_status=401,
        )
    try:
        return int(token.split(":", 1)[1])
    except ValueError:
        raise AppError(
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
            message="Invalid token user_id",
            http_status=401,
        )

def get_user_by_token(db: Session, token: str) -> User:
    user_id = parse_token(token)
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise AppError(
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
            message="User not found for token",
            http_status=401,
        )
    return user
