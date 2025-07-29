-- roles
CREATE TABLE IF NOT EXISTS roles (
  role_id   SERIAL PRIMARY KEY,
  role_name TEXT NOT NULL UNIQUE  -- e.g. 'admin','recruiter','manager','viewer'
);
-- users
CREATE TABLE IF NOT EXISTS users (
  user_id    SERIAL PRIMARY KEY,
  username   TEXT NOT NULL UNIQUE,
  full_name  TEXT,
  email      TEXT NOT NULL UNIQUE,
  hashed_pw  TEXT NOT NULL,
  is_active  BOOLEAN NOT NULL DEFAULT TRUE
);
-- mapping
CREATE TABLE IF NOT EXISTS user_roles (
  user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role_id INT NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);