# src/services/access_control_service.py
from fastapi import HTTPException, status
from typing import List
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.schemas.auth import User as UserSchema

class AccessControlService:
    @staticmethod
    def check_roles(user: UserSchema, allowed_roles: List[str]) -> None:
        """
        Verify the user has at least one of the allowed roles.
        """
        user_role_names = [role.role_name for role in user.roles]
        if not any(r in allowed_roles for r in user_role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges"
            )