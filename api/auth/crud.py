# api/auth/crud.py

import os
import psycopg2
from typing import Optional
from dotenv import load_dotenv
from passlib.context import CryptContext

from .schemas import UserInDB

# Load environment variables
load_dotenv()
DB_DSN = os.getenv("DB_DSN", "postgresql://jd_user:jd_pass@localhost:5432/jd_library")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(username: str) -> Optional[UserInDB]:
    """
    Fetch a user by username from the database, including their roles.
    Returns a UserInDB instance or None if not found.
    """
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    cur.execute("""
        SELECT u.user_id, u.username, u.full_name, u.email, u.hashed_pw, u.is_active,
               array_agg(r.role_name)
        FROM users u
        JOIN user_roles ur ON u.user_id = ur.user_id
        JOIN roles r ON ur.role_id = r.role_id
        WHERE u.username = %s
        GROUP BY u.user_id;
    """, (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    return UserInDB(
        user_id   = row[0],
        username  = row[1],
        full_name = row[2],
        email     = row[3],
        hashed_pw = row[4],
        is_active = row[5],
        roles     = row[6] or []
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored bcrypt hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    return pwd_context.hash(password)