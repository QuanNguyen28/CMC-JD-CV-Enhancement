# src/api/dependencies.py
"""
Dependencies for FastAPI endpoints:
- Database session management (SQLAlchemy)
- Authentication and RBAC (JWT)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.db.session import get_db
from src.crud.auth_crud import get_user
from src.schemas.auth import TokenData, User as UserSchema
from src.core.config import JWT_SECRET_KEY, ALGORITHM

from src.services.access_control_service import AccessControlService

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserSchema:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError()
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user = get_user(db, token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

def require_roles(*roles: str):
    """
    Dependency factory ensuring the current user has one of the specified roles.
    Usage: Depends(require_roles("admin", "recruiter"))
    """
    def checker(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
        AccessControlService.check_roles(current_user, list(roles))
        return current_user
    return checker