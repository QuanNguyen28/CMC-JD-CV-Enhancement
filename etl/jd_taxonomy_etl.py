# etl/jd_taxonomy_etl.py
#!/usr/bin/env python
"""
ETL to load Job Families & Taxonomy Tags from Markdown frontmatter
"""
import os
import glob
import sys
from dotenv import load_dotenv
load_dotenv()

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import frontmatter
import psycopg2
from src.core.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

def main():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()

    # ensure families and tags tables exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_families (
      family_id   SERIAL PRIMARY KEY,
      name        TEXT NOT NULL UNIQUE,
      description TEXT
    );
    CREATE TABLE IF NOT EXISTS jd_taxonomy_tags (
      tag_id        SERIAL PRIMARY KEY,
      tag_name      TEXT NOT NULL UNIQUE,
      description   TEXT,
      parent_tag_id INT REFERENCES jd_taxonomy_tags(tag_id)
    );
    """)
    conn.commit()

    # scan markdown for unique families and tags
    md_dir = os.path.join(os.path.dirname(__file__), 'jd_markdown')
    md_files = glob.glob(os.path.join(md_dir, '*.md'))

    families = set()
    tags = set()
    for md_file in md_files:
        post = frontmatter.load(md_file)
        meta = post.metadata
        if meta.get('family'):
            families.add(meta['family'])
        for t in meta.get('tags', []):
            tags.add(t)

    # upsert families
    for fam in families:
        cur.execute("INSERT INTO job_families(name) VALUES(%s) ON CONFLICT(name) DO NOTHING;", (fam,))
    # upsert tags
    for t in tags:
        cur.execute("INSERT INTO jd_taxonomy_tags(tag_name) VALUES(%s) ON CONFLICT(tag_name) DO NOTHING;", (t,))
    conn.commit()

    print(f"🎉 Loaded {len(families)} families and {len(tags)} taxonomy tags.")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()