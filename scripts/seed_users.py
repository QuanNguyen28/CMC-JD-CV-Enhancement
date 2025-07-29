# chỉ chạy một lần
from passlib.context import CryptContext
import psycopg2, os
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
conn = psycopg2.connect(os.getenv("DB_DSN"))
cur = conn.cursor()
# seed roles
for r in ("admin","recruiter","manager","viewer"):
    cur.execute("INSERT INTO roles (role_name) VALUES (%s) ON CONFLICT DO NOTHING", (r,))
# seed an admin user
pw = pwd_ctx.hash("changeme")
cur.execute("""
  INSERT INTO users (username, full_name, email, hashed_pw)
  VALUES ('hr_admin','HR Admin','hr@company.com',%s)
  ON CONFLICT DO NOTHING
""", (pw,))
# assign admin role
cur.execute("""
  INSERT INTO user_roles (user_id, role_id)
  SELECT u.user_id, r.role_id
  FROM users u, roles r
  WHERE u.username='hr_admin' AND r.role_name='admin'
  ON CONFLICT DO NOTHING
""")
conn.commit()
cur.close(); conn.close()