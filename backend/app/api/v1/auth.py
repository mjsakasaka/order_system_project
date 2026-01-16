from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.auth import LoginRequest, LoginResponse
from ...services.auth_service import login, issue_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login_api(payload: LoginRequest, db: Session = Depends(get_db)):
    user = login(db, payload.username, payload.password)
    return LoginResponse(access_token=issue_token(user), role=user.role)

from ...api.deps import get_current_user
from ...schemas.user import UserOut

@router.get("/me", response_model=UserOut)
def me(user = Depends(get_current_user)):
    return UserOut(id=user.id, username=user.username, role=user.role)
