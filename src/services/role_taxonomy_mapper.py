# src/services/role_taxonomy_mapper.py
"""
Map user-provided role names to internal taxonomy metadata.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.crud.role_crud import get_role_by_name

class RoleTaxonomyMapper:
    @staticmethod
    def map_role_to_taxonomy(db: Session, role_name: str) -> Dict[str, Any]:
        """
        Map a role name to its taxonomy information stored in the database.

        Args:
            db: SQLAlchemy session
            role_name: The name of the role to look up

        Returns:
            A dict containing role taxonomy details: role_name and optional description.

        Raises:
            ValueError: If the role is not found.
        """
        role = get_role_by_name(db, role_name)
        if role is None:
            raise ValueError(f"Role '{role_name}' not found in taxonomy.")
        return {
            "role_name": role.role_name,
            "description": getattr(role, 'description', None)
        }
# src/services/role_taxonomy_mapper.py
"""
Role ↔ Job Family mapper utilities.

- get_or_create_family(db, family_name) -> Optional[int]
  Returns existing JobFamily.family_id (case-insensitive) or creates a new one.

- RoleTaxonomyMapper.map_role_to_taxonomy(db, role_name) -> Dict
  Fetches basic role taxonomy info from DB (role_name + optional description).
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db.models import JobFamily as DBJobFamily, Role as DBRole


def _normalize(text: str) -> str:
    return " ".join(text.strip().split())


def get_or_create_family(db: Session, family_name: Optional[str]) -> Optional[int]:
    """
    Return family_id for given job family name (case-insensitive).
    If name is empty -> return None. If not exists -> create and return new id.
    """
    if not family_name or not str(family_name).strip():
        return None
    norm = _normalize(str(family_name))
    existing = (
        db.query(DBJobFamily)
        .filter(func.lower(DBJobFamily.name) == norm.lower())
        .first()
    )
    if existing:
        return existing.family_id
    fam = DBJobFamily(name=norm, description=None)
    db.add(fam)
    db.commit()
    db.refresh(fam)
    return fam.family_id


class RoleTaxonomyMapper:
    @staticmethod
    def get_or_create_family(db: Session, family_name: Optional[str]) -> Optional[int]:
        return get_or_create_family(db, family_name)

    @staticmethod
    def map_role_to_taxonomy(db: Session, role_name: str) -> Dict[str, Any]:
        """
        Return basic taxonomy info for a role. Raises ValueError if not found.
        """
        if not role_name or not role_name.strip():
            raise ValueError("role_name is required")
        norm = _normalize(role_name)
        role = (
            db.query(DBRole)
            .filter(func.lower(DBRole.role_name) == norm.lower())
            .first()
        )
        if role is None:
            raise ValueError(f"Role '{role_name}' not found in taxonomy.")
        return {
            "role_name": role.role_name,
            "description": getattr(role, "description", None),
        }