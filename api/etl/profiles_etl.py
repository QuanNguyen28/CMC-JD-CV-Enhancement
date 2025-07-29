#!/usr/bin/env python
"""
api/etl/profiles_etl.py

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
from passlib.context import CryptContext

def main():
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "jd_library")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        database=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()

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

    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def parse_skills(raw: str):
        return [s.strip() for s in raw.split(",") if s.strip()]

    csv_files = glob.glob("candidate_data/*.csv")
    total = 0

    for path in csv_files:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                full_name   = row.get("full_name","")
                email       = row.get("email","")
                phone       = row.get("phone","")
                resume_text = row.get("resume_text","")
                skills_raw  = row.get("skills","")

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

                cur.execute("SELECT candidate_id FROM candidate_profiles WHERE email = %s", (email,))
                candidate_id = cur.fetchone()[0]

                skills = parse_skills(skills_raw)
                for skill in skills:
                    cur.execute(
                        "INSERT INTO skills_master (skill_name) VALUES (%s) ON CONFLICT (skill_name) DO NOTHING;",
                        (skill,)
                    )
                conn.commit()

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

    cur.close()
    conn.close()
    print(f"✅ ETL completed: Imported/Updated {total} candidate profiles.")

if __name__ == "__main__":
    main()