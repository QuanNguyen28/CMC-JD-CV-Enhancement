-- Create table for candidate profiles
CREATE TABLE IF NOT EXISTS candidate_profiles (
  candidate_id     SERIAL PRIMARY KEY,
  full_name        TEXT NOT NULL,
  email            VARCHAR(255) UNIQUE NOT NULL,
  phone            VARCHAR(50),
  resume_text      TEXT NOT NULL,        -- Parsed plain text of resume
  created_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Optional: separate skills table and mapping
CREATE TABLE IF NOT EXISTS skills_master (
  skill_id   SERIAL PRIMARY KEY,
  skill_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS candidate_skills (
  candidate_id INT NOT NULL REFERENCES candidate_profiles(candidate_id) ON DELETE CASCADE,
  skill_id     INT NOT NULL REFERENCES skills_master(skill_id) ON DELETE CASCADE,
  PRIMARY KEY(candidate_id, skill_id)
);
