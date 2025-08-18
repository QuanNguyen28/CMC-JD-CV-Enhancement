-- seed.sql
SET search_path TO smarthire, public;  -- <== ghi thẳng schema của bạn

INSERT INTO roles (role_name) VALUES ('admin')     ON CONFLICT DO NOTHING;
INSERT INTO roles (role_name) VALUES ('recruiter') ON CONFLICT DO NOTHING;

-- NHỚ thay hash thật
INSERT INTO users (username, full_name, email, hashed_pw, is_active)
VALUES ('kkcom', 'kkcom HR', 'kkcom@example.com', '$2b$12$uWUMvnWroN5nv7Hjv8EsUOveL4gCoPPmMMPzs/A89sHSloabnDvHW', true)
ON CONFLICT (username) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.user_id, r.role_id
FROM users u, roles r
WHERE u.username='kkcom' AND r.role_name='admin'
ON CONFLICT DO NOTHING;