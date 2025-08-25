from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from src.api.dependencies import get_db, get_current_user
from src.crud.auth_crud import authenticate_user
from src.schemas.auth import Token, User
from src.core.config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Auth"])

def _create_access_token(data: dict, minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.post("/token", response_model=Token)
def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    roles = [r.role_name for r in getattr(user, "roles", [])]
    # IMPORTANT: để claim 'sub' là username — get_current_user sẽ đọc từ đây
    access_token = _create_access_token({"sub": user.username, "roles": roles})

    # để Swagger/FE khỏi nhầm, luôn trả “Bearer” (viết hoa B)
    return {"access_token": access_token, "token_type": "Bearer"}

@router.get("/me", response_model=User)
def me(current_user: User = Depends(get_current_user)):
    return current_user