#!/usr/bin/env python
"""
etl/jd_etl.py

ETL script to load Job Description Markdown files into PostgreSQL,
and maintain version history in jd_versions.
"""

import glob
import os
import frontmatter
import psycopg2
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()  # expects .env in project root

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

# 3. Ensure job_families, job_descriptions, jd_versions, jd_taxonomy_tags, jd_tag_map exist
#    Assumes migrations have been run. If not, you could execute DDL here.

# 4. Process Markdown files
md_files = glob.glob('jd_markdown/*.md')
for md_file in md_files:
    post = frontmatter.load(md_file)
    meta, content_md = post.metadata, post.content

    job_code = meta['job_code']
    title = meta['title']
    department = meta.get('department')
    family = meta.get('family')
    level = meta.get('level')
    employment_type = meta.get('employment_type')
    location = meta.get('location')
    created_by = meta.get('created_by', 'etl_script')

    # 4.1 Upsert job family
    cur.execute(
        "INSERT INTO job_families(name) VALUES (%s) ON CONFLICT(name) DO NOTHING;",
        (family,)
    )
    conn.commit()
    cur.execute("SELECT family_id FROM job_families WHERE name=%s;", (family,))
    family_id = cur.fetchone()[0]

    # 4.2 Upsert main job_description
    cur.execute("""
        INSERT INTO job_descriptions
          (job_code, title, department, family_id, level,
           employment_type, location, content_md, version, created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1,%s)
        ON CONFLICT(job_code) DO UPDATE
          SET content_md = EXCLUDED.content_md,
              version = job_descriptions.version + 1,
              updated_at = NOW();
    """, (
        job_code, title, department, family_id, level,
        employment_type, location, content_md, created_by
    ))
    conn.commit()

    # 4.3 Retrieve jd_id and current version
    cur.execute(
        "SELECT jd_id, version FROM job_descriptions WHERE job_code=%s;",
        (job_code,)
    )
    jd_id, version = cur.fetchone()

    # 4.4 Insert into jd_versions for history
    cur.execute("""
        INSERT INTO jd_versions
          (jd_id, version_number, content_md, edited_by, change_summary)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (jd_id, version_number) DO NOTHING;
    """, (
        jd_id,
        version,
        content_md,
        created_by,
        f"ETL import, version {version}"
    ))
    conn.commit()

    # 4.5 Upsert taxonomy tags and mapping
    tags = meta.get('tags', [])
    for tag in tags:
        cur.execute(
            "INSERT INTO jd_taxonomy_tags(tag_name) VALUES (%s) ON CONFLICT(tag_name) DO NOTHING;",
            (tag,)
        )
    conn.commit()

    # Map tags to this JD
    for tag in tags:
        cur.execute(
            "SELECT tag_id FROM jd_taxonomy_tags WHERE tag_name=%s;",
            (tag,)
        )
        tag_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO jd_tag_map(jd_id, tag_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (jd_id, tag_id))
    conn.commit()

print(f"✅ ETL completed: imported {len(md_files)} JD files with versioning.")
cur.close()
conn.close()
