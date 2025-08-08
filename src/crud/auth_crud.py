# src/crud/auth_crud.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.db.models import User as DBUser
from src.schemas.auth import UserCreate
from src.core.config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication & Token Functions

def get_user(db: Session, username: str) -> Optional[DBUser]:
    """Retrieve a user by username."""
    return db.query(DBUser).filter(DBUser.username == username).first()


def create_user(db: Session, user: UserCreate) -> DBUser:
    """Create a new user with hashed password."""
    hashed_pw = pwd_context.hash(user.password)
    db_user = DBUser(
        username=user.username,
        hashed_pw=hashed_pw,
        full_name=user.full_name,
        email=user.email,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[DBUser]:
    """Verify username/password and return user if valid."""
    user = get_user(db, username)
    if not user or not pwd_context.verify(password, user.hashed_pw):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt