#!/usr/bin/env python
"""
etl/profiles_etl.py

ETL script to load candidate profiles from CSV files into PostgreSQL:
- candidate_profiles
- skills_master
- candidate_skills
"""

import os
import glob
import csv
import psycopg2
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "jd_library")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# 2. Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST, port=DB_PORT,
    database=DB_NAME, user=DB_USER, password=DB_PASS
)
cur = conn.cursor()

# 3. Create tables if they don't exist
ddl = """
CREATE TABLE IF NOT EXISTS candidate_profiles (
  candidate_id     SERIAL PRIMARY KEY,
  full_name        TEXT NOT NULL,
  email            VARCHAR(255) UNIQUE NOT NULL,
  phone            VARCHAR(50),
  resume_text      TEXT NOT NULL,
  created_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills_master (
  skill_id   SERIAL PRIMARY KEY,
  skill_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS candidate_skills (
  candidate_id INT NOT NULL REFERENCES candidate_profiles(candidate_id) ON DELETE CASCADE,
  skill_id     INT NOT NULL REFERENCES skills_master(skill_id) ON DELETE CASCADE,
  PRIMARY KEY (candidate_id, skill_id)
);
"""
cur.execute(ddl)
conn.commit()

# 4. Helper to parse skills string into list
def parse_skills(raw_skills: str) -> list[str]:
    # Expecting comma-separated skills
    if not raw_skills:
        return []
    return [s.strip() for s in raw_skills.split(",") if s.strip()]

# 5. Process all CSV files in candidate_data/
csv_files = glob.glob("candidate_data/*.csv")
total = 0

for csv_file in csv_files:
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_name   = row.get("full_name") or row.get("name") or ""
            email       = row.get("email") or ""
            phone       = row.get("phone") or ""
            resume_text = row.get("resume_text") or row.get("bio") or ""
            skills_raw  = row.get("skills") or ""

            # Insert candidate_profile
            cur.execute(
                """
                INSERT INTO candidate_profiles (full_name, email, phone, resume_text)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE
                  SET full_name = EXCLUDED.full_name,
                      phone      = EXCLUDED.phone,
                      resume_text= EXCLUDED.resume_text;
                """,
                (full_name, email, phone, resume_text)
            )
            conn.commit()

            # Retrieve candidate_id
            cur.execute("SELECT candidate_id FROM candidate_profiles WHERE email = %s", (email,))
            candidate_id = cur.fetchone()[0]

            # Upsert skills and mapping
            skills = parse_skills(skills_raw)
            for skill in skills:
                # upsert into skills_master
                cur.execute(
                    "INSERT INTO skills_master (skill_name) VALUES (%s) ON CONFLICT (skill_name) DO NOTHING;",
                    (skill,)
                )
            conn.commit()

            # Map skills to candidate
            for skill in skills:
                cur.execute(
                    "SELECT skill_id FROM skills_master WHERE skill_name = %s;",
                    (skill,)
                )
                skill_id = cur.fetchone()[0]
                cur.execute(
                    """
                    INSERT INTO candidate_skills (candidate_id, skill_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (candidate_id, skill_id)
                )
            conn.commit()

            total += 1

print(f"✅ ETL completed: Imported/Updated {total} candidate profiles.")

cur.close()
conn.close()
