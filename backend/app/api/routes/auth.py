from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.core.security import create_access_token, verify_password
from backend.app.db.models import User
from backend.app.schemas.auth import AuthResponse, LoginRequest, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.query(User).filter(User.username == payload.username).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.username)
    return AuthResponse(
        access_token=token,
        user=UserResponse(id=user.id, username=user.username, role=user.role),
    )


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=current_user.id, username=current_user.username, role=current_user.role)
