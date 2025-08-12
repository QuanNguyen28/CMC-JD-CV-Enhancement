# src/api/v1/roles.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.api.dependencies import get_db, require_roles
from src.schemas.roles import RoleListResponse
from src.crud.role_crud import list_roles

router = APIRouter(prefix="/v1/roles", tags=["Roles"])

@router.get("/list", response_model=List[RoleListResponse])
def get_roles(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "recruiter", "manager"))
):
    return list_roles(db)