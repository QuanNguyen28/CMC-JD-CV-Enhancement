# src/crud/role_crud.py
from sqlalchemy.orm import Session
from src.db.models import Role as DBRole
from src.schemas.roles import RoleListResponse
from typing import List, Optional

def list_roles(db: Session) -> List[RoleListResponse]:
    roles = db.query(DBRole).all()
    return [RoleListResponse(role_name=r.name, description=r.description) for r in roles]

def get_role_by_name(db: Session, role_name: str) -> Optional[DBRole]:
    """Retrieve a role by name."""
    return db.query(DBRole).filter(DBRole.role_name == role_name).first()