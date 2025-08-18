from sqlalchemy import text
from src.db.session import SessionLocal

HASH = "$2b$12$uWUMvnWroN5nv7Hjv8EsUOveL4gCoPPmMMPzs/A89sHSloabnDvHW"  # dán hash mới
SQL = """
SET search_path TO smarthire, public;
UPDATE users SET hashed_pw = :hash WHERE username = 'alice';
UPDATE users SET is_active = TRUE WHERE username = 'alice';
"""

with SessionLocal() as db:
    db.execute(text(SQL), {"hash": HASH})
    db.commit()
print("Password updated.")