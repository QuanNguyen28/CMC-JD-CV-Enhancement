# src/api/dependencies.py
"""
Dependencies for FastAPI endpoints:
- Database session (SQLAlchemy)
- OAuth2 bearer token
- Current user & RBAC
"""
from typing import Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from src.db.session import SessionLocal
from src.core.config import JWT_SECRET_KEY, ALGORITHM
from src.schemas.auth import User as UserSchema, TokenData
from src.db.models import User as DBUser, Role as DBRole
from src.crud.auth_crud import get_user  # <- chỉ cần get_user, tránh import vòng tròn

# --- DB session dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- OAuth2 scheme ---
# NOTE: tokenUrl phải trỏ tới đúng route bạn đã khai báo trong auth.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Current user from Bearer token ---
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserSchema:
    """
    Decode JWT từ header Authorization: Bearer <token>, lấy user từ DB,
    rồi map sang UserSchema (pydantic) để trả về.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user: DBUser | None = get_user(db, token_data.username)
    if user is None or user.is_active is False:
        raise credentials_exception

    # Map sang schema (roles -> list[str]) nhờ validator + orm_mode
    return UserSchema.model_validate(user, from_attributes=True)

# --- RBAC helper ---
def require_roles(*allowed: str) -> Callable:
    """
    Usage:
      Depends(require_roles("admin", "recruiter"))
    """
    allowed_set = set(a.lower() for a in allowed)

    def _checker(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
        user_roles = set((current_user.roles or []))
        # current_user.roles đã là list[str] (validator trong schemas.auth)
        if not (user_roles & allowed_set):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _checker