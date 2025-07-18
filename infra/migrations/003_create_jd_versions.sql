-- infra/migrations/003_create_jd_versions.sql

-- 1. Create table to store all versions of a job description
CREATE TABLE IF NOT EXISTS jd_versions (
  version_id     SERIAL PRIMARY KEY,
  jd_id           INT NOT NULL
                   REFERENCES job_descriptions(jd_id)
                   ON UPDATE CASCADE
                   ON DELETE CASCADE,
  version_number  INT NOT NULL,
  content_md      TEXT NOT NULL,             -- Markdown content at this version
  edited_by       VARCHAR(50) NOT NULL,      -- Username who made the change
  edited_at       TIMESTAMP NOT NULL
                   DEFAULT NOW(),           -- When the change was made
  change_summary  TEXT,                     
  UNIQUE (jd_id, version_number)
);

-- 2. Add a column to job_descriptions to track the current version
ALTER TABLE job_descriptions
  ADD COLUMN IF NOT EXISTS current_version INT NOT NULL DEFAULT 1;

-- 3. (Optional) Insert the initial version for existing JDs
INSERT INTO jd_versions (jd_id, version_number, content_md, edited_by, change_summary)
SELECT jd_id, 1, content_md, created_by, 'Initial version'
FROM job_descriptions
ON CONFLICT (jd_id, version_number) DO NOTHING;
