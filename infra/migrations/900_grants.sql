-- search_path đã set; nhưng GRANT có thể cần fully qualified khi cấp cho user khác
-- ví dụ cấp cho user ứng dụng chính (đổi tên phù hợp):
-- GRANT USAGE ON SCHEMA :"schema" TO smarthire_app;
-- GRANT CREATE ON SCHEMA :"schema" TO smarthire_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO CURRENT_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO CURRENT_USER;

-- nếu muốn set owner tất cả bảng về CURRENT_USER:
-- DO $$
-- DECLARE r record;
-- BEGIN
--   FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = current_schema() LOOP
--     EXECUTE format('ALTER TABLE %I OWNER TO %I', r.tablename, current_user);
--   END LOOP;
-- END$$;