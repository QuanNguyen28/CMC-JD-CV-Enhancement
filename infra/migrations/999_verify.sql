SELECT current_database() AS db,
       current_user      AS "user",
       current_schema()  AS schema;

SHOW search_path;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = current_schema()
ORDER BY table_name;

-- kiểm tra cột/constraints chính
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = current_schema()
  AND table_name IN ('job_descriptions','jd_versions','jd_taxonomy_tags','jd_tag_map','job_families','users','roles','user_roles')
ORDER BY table_name, ordinal_position;

-- unique keys quan trọng
SELECT i.relname AS index_name, t.relname AS table_name, a.attname AS column_name
FROM   pg_class t, pg_class i, pg_index ix, pg_attribute a
WHERE  t.oid = ix.indrelid
AND    i.oid = ix.indexrelid
AND    a.attrelid = t.oid
AND    a.attnum = ANY(ix.indkey)
AND    t.relkind = 'r'
AND    t.relname IN ('job_descriptions','jd_versions','jd_taxonomy_tags','users','roles')
ORDER BY t.relname, i.relname, a.attnum;