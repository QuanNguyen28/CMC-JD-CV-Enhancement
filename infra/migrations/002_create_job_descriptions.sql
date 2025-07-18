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

-- Main Job Descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
  jd_id           SERIAL PRIMARY KEY,
  job_code        VARCHAR(50) NOT NULL UNIQUE,
  title           TEXT NOT NULL,
  department      TEXT,
  family_id       INT REFERENCES job_families(family_id),
  level           VARCHAR(20),
  employment_type VARCHAR(20),
  location        TEXT,
  content_md      TEXT NOT NULL,         -- Markdown content
  version         INT NOT NULL DEFAULT 1,
  created_by      VARCHAR(50),
  created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Mapping table between JDs and taxonomy tags
CREATE TABLE IF NOT EXISTS jd_tag_map (
  jd_id INT REFERENCES job_descriptions(jd_id) ON DELETE CASCADE,
  tag_id INT REFERENCES jd_taxonomy_tags(tag_id) ON DELETE CASCADE,
  PRIMARY KEY (jd_id, tag_id)
);
