# etl/profiles_etl.py
#!/usr/bin/env python
"""
ETL script to load Candidate Profiles from CSV and document files
Tables: candidate_profiles, skills_master, candidate_skills
"""
import os
import glob
import sys
import csv
from dotenv import load_dotenv
load_dotenv()

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import psycopg2
from src.core.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
from src.utils.file_extract import extract_text_from_file

def main():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()

    # ensure tables exist
    sql = open(os.path.join('infra', 'migrations', '001_create_candidate_profiles.sql')).read()
    cur.execute(sql)
    conn.commit()

    # load CSV data
    data_dir = os.path.join(os.path.dirname(__file__), 'candidate_data')
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    for csv_file in csv_files:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email      = row.get('email')
                full_name  = row.get('full_name')
                phone      = row.get('phone')
                resume_src = row.get('resume_file')  # optional
                resume_text = ''
                if resume_src and os.path.isfile(resume_src):
                    with open(resume_src, 'rb') as rf:
                        resume_text = extract_text_from_file(rf.read(), resume_src)
                cur.execute(
                    "INSERT INTO candidate_profiles(full_name,email,phone,resume_text) "
                    "VALUES(%s,%s,%s,%s) ON CONFLICT(email) DO UPDATE SET resume_text=EXCLUDED.resume_text;",
                    (full_name, email, phone, resume_text)
                )
    conn.commit()

    # map skills
    if csv_files:
        reader = csv.DictReader(open(csv_files[0], newline='', encoding='utf-8'))
        skills_set = set()
        profile_skills = []
        for row in reader:
            email = row.get('email')
            for skill in row.get('skills', '').split(';'):
                s = skill.strip()
                if s:
                    skills_set.add(s)
                    profile_skills.append((email, s))
        for skill in skills_set:
            cur.execute("INSERT INTO skills_master(skill_name) VALUES(%s) ON CONFLICT(skill_name) DO NOTHING;", (skill,))
        conn.commit()
        for email, skill in profile_skills:
            cur.execute("SELECT candidate_id FROM candidate_profiles WHERE email=%s;", (email,))
            cid = cur.fetchone()[0]
            cur.execute("SELECT skill_id FROM skills_master WHERE skill_name=%s;", (skill,))
            sid = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO candidate_skills(candidate_id,skill_id) VALUES(%s,%s) ON CONFLICT DO NOTHING;",
                (cid, sid)
            )
        conn.commit()

    print("🎉 ETL complete: loaded candidate profiles and skills.")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()