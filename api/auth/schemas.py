# api/auth/schemas.py

from typing import List, Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []

class User(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str] = None
    email: str
    is_active: bool
    roles: List[str] = []

class UserInDB(User):
    hashed_pw: str