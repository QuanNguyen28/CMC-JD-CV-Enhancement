# scripts/seed_users.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bcrypt
from sqlalchemy.exc import IntegrityError
from src.db.session import SessionLocal
from src.db.models import User, Role, UserRole

def create_user(username, password, full_name, email, roles):
    db = SessionLocal()
    try:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            hashed_pw=hashed_pw,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        user = db.query(User).filter_by(username=username).first()
        print(f"User '{username}' already exists, skipping creation.")
    # Gán roles (tương tự upsert)
    for role_name in roles:
        role = db.query(Role).filter_by(role_name=role_name).first()
        if role and not any(ur.role_id == role.role_id for ur in user.roles):
            db.add(UserRole(user_id=user.user_id, role_id=role.role_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    db.close()
    print(f"Seeded user {username} with roles {roles}")

if __name__ == "__main__":
    create_user(
        username="hr_admin",
        password="changeme",
        full_name="HR Admin",
        email="admin@example.com",
        roles=["admin", "recruiter"]
    )