# src/services/role_taxonomy_mapper.py
"""
Map user-provided role names to internal taxonomy metadata.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
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