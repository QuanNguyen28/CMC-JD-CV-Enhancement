# src/services/__init__.py
"""
SmartHire Composer - services package.

⚠️ Tránh import các module con tại đây để không tạo circular import.
Hãy import trực tiếp ở nơi sử dụng, ví dụ:
  - from src.services.access_control_service import AccessControlService
  - from src.services.jd_versioning_service import record_jd_version, get_versions, update_jd
  - from src.services.export_bridge import export_jd_file
  - from src.services.llm_prompt_orchestrator import generate_jd_text, improve_jd_text
"""

from typing import TYPE_CHECKING

# Chỉ để IDE/type check; KHÔNG import thật khi chạy runtime
if TYPE_CHECKING:
    from .access_control_service import AccessControlService
    from .jd_versioning_service import record_jd_version, get_versions, update_jd
    from .export_bridge import export_jd_file
    from .llm_prompt_orchestrator import generate_jd_text, improve_jd_text

__all__: list[str] = []  # không re-export để tránh side effects