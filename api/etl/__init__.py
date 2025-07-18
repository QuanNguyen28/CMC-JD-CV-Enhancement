# etl/__init__.py
"""
ETL package: scripts to ingest JD Markdown and candidate data into PostgreSQL.
"""

from .jd_etl import main as run_jd_etl
from .profiles_etl import main as run_profiles_etl

__all__ = [
    "run_jd_etl",
    "run_profiles_etl",
]
