#!/usr/bin/env python
"""
etl/jd_taxonomy_etl.py

ETL script to load Job Descriptions (Markdown) and their taxonomy tags
into PostgreSQL tables:
  - job_families
  - jd_taxonomy_tags
  - job_descriptions
  - jd_tag_map
"""

import os
import glob
import frontmatter
import psycopg2
from dotenv import load_dotenv

# 1. Load .env
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

# 3. Create tables if not exist
ddl = """
-- Job Families
CREATE TABLE IF NOT EXISTS job_families (
  family_id   SERIAL PRIMARY KEY,
  name        TEXT NOT NULL UNIQUE,
  description TEXT
);

-- Taxonomy Tags
CREATE TABLE IF NOT EXISTS jd_taxonomy_tags (
  tag_id        SERIAL PRIMARY KEY,
  tag_name      TEXT NOT NULL UNIQUE,
  description   TEXT,
  parent_tag_id INT REFERENCES jd_taxonomy_tags(tag_id)
);

-- Job Descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
  jd_id           SERIAL PRIMARY KEY,
  job_code        VARCHAR(50) NOT NULL UNIQUE,
  title           TEXT NOT NULL,
  department      TEXT,
  family_id       INT REFERENCES job_families(family_id),
  level           VARCHAR(20),
  employment_type VARCHAR(20),
  location        TEXT,
  content_md      TEXT NOT NULL,
  version         INT NOT NULL DEFAULT 1,
  created_by      VARCHAR(50),
  created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMP        -- updated on version bump
);

-- Mapping JD ↔ Tags
CREATE TABLE IF NOT EXISTS jd_tag_map (
  jd_id INT REFERENCES job_descriptions(jd_id) ON DELETE CASCADE,
  tag_id INT REFERENCES jd_taxonomy_tags(tag_id) ON DELETE CASCADE,
  PRIMARY KEY (jd_id, tag_id)
);
"""
cur.execute(ddl)
conn.commit()

# 4. ETL: parse each Markdown in jd_markdown/
md_dir = "jd_markdown"
md_files = glob.glob(os.path.join(md_dir, "*.md"))

for md_file in md_files:
    post = frontmatter.load(md_file)
    meta = post.metadata
    content = post.content.strip()

    # Required metadata keys: job_code, title, family, tags (list)
    job_code   = meta.get("job_code")
    title      = meta.get("title")
    department = meta.get("department")
    family     = meta.get("family")
    level      = meta.get("level")
    emp_type   = meta.get("employment_type")
    location   = meta.get("location")
    created_by = meta.get("created_by", "etl_script")
    tags       = meta.get("tags", [])

    if not job_code or not title or not family:
        print(f"⚠️  Skipping {md_file}: missing job_code/title/family")
        continue

    # Upsert family
    cur.execute(
        "INSERT INTO job_families (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
        (family,)
    )
    conn.commit()
    cur.execute("SELECT family_id FROM job_families WHERE name = %s;", (family,))
    family_id = cur.fetchone()[0]

    # Upsert tags
    for tag in tags:
        cur.execute(
            "INSERT INTO jd_taxonomy_tags (tag_name) VALUES (%s) ON CONFLICT (tag_name) DO NOTHING;",
            (tag,)
        )
    conn.commit()

    # Upsert JD
    cur.execute(
        """
        INSERT INTO job_descriptions
          (job_code, title, department, family_id, level, employment_type, location,
           content_md, version, created_by, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1,%s,NOW())
        ON CONFLICT (job_code) DO UPDATE
          SET content_md = EXCLUDED.content_md,
              version    = job_descriptions.version + 1,
              updated_at = NOW();
        """,
        (
            job_code, title, department, family_id, level,
            emp_type, location, content, created_by
        )
    )
    conn.commit()

    # Retrieve jd_id
    cur.execute("SELECT jd_id FROM job_descriptions WHERE job_code = %s;", (job_code,))
    jd_id = cur.fetchone()[0]

    # Map tags
    for tag in tags:
        cur.execute(
            "SELECT tag_id FROM jd_taxonomy_tags WHERE tag_name = %s;",
            (tag,)
        )
        tag_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO jd_tag_map (jd_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (jd_id, tag_id)
        )
    conn.commit()

    print(f"✅ Processed JD: {job_code} (ID {jd_id})")

# 5. Cleanup
cur.close()
conn.close()
print(f"🎉 ETL complete: processed {len(md_files)} JD files.")
