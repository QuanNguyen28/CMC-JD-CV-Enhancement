# src/crud/__init__.py
"""
CRUD package initializer: expose key CRUD functions.
"""
from .auth_crud      import get_user, create_user, authenticate_user, create_access_token
from .jd_crud        import create_jd, get_jd_content, list_all_jds
from .version_crud   import create_version, get_versions_by_jd_id, get_all_chunks
from .role_crud      import list_roles
# interview_crud no longer exported
# from .interview_crud import save_interview_questions

__all__ = [
    "get_user", "create_user", "authenticate_user", "create_access_token",
    "create_jd", "get_jd_content", "list_all_jds",
    "create_version", "get_versions_by_jd_id", "get_all_chunks",
    "list_roles",
]