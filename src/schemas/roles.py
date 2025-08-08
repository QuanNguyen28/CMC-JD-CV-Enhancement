# src/schemas/roles.py
from pydantic import BaseModel
from typing import List, Optional

class RoleListResponse(BaseModel):
    role_name: str
    description: Optional[str]