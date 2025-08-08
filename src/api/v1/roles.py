# src/api/v1/roles.py
from fastapi import APIRouter, Depends
from typing import List

from src.schemas.roles import RoleListResponse
from src.crud.role_crud import list_roles
from src.api.dependencies import require_roles

router = APIRouter(prefix="/v1/roles", tags=["Roles"])

@router.get("/list", response_model=List[RoleListResponse])
def get_roles(
    current_user = Depends(require_roles("admin", "recruiter", "viewer"))
) -> List[RoleListResponse]:
    """
    Retrieve all available roles and their descriptions.
    """
    return list_roles()