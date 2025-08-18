CREATE TABLE IF NOT EXISTS candidate_skills (
  candidate_id INTEGER NOT NULL REFERENCES candidate_profiles(candidate_id) ON DELETE CASCADE,
  skill_id     INTEGER NOT NULL REFERENCES skills_master(skill_id) ON DELETE CASCADE,
  PRIMARY KEY(candidate_id, skill_id)
);