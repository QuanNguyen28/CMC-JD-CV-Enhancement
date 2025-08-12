# src/crud/role_crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
from src.db.models import Role as DBRole
from src.schemas.roles import RoleListResponse

def list_roles(db: Session) -> List[RoleListResponse]:
    rows = db.query(DBRole).all()
    # description có thể không tồn tại trong DB -> getattr cho an toàn
    return [
        RoleListResponse(
            role_name=r.role_name,
            description=getattr(r, "description", None)
        )
        for r in rows
    ]

def get_role_by_name(db: Session, role_name: str) -> Optional[DBRole]:
    """Retrieve a role by name."""
    return db.query(DBRole).filter(DBRole.role_name == role_name).first()