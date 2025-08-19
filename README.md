# SmartHire Composer — JD & Interview Enhancement

**SmartHire Composer** là trợ lý AI hỗ trợ HR/Hiring Manager tạo **Job Description (JD)** chuẩn hóa và sinh **câu hỏi phỏng vấn** theo vai trò, đồng thời quản lý **phiên bản** và hỗ trợ **tìm kiếm ngữ nghĩa (RAG)** qua **Milvus**.

- Backend: **FastAPI (Python)**
- CSDL chính: **AWS RDS PostgreSQL** (schema riêng `smarthire`)
- Vector store: **Milvus** chạy trên **EC2**
- JD mẫu & chunk: **lưu local** (không dùng MinIO/S3 trong bản này)
- Auth & RBAC: JWT với các vai trò `admin`, `recruiter`, `manager`, `viewer`

---

## 1) Tính năng
- **JD Composer**: tạo JD mới từ `title / department / level / job_family` + gợi ý AI (Gemini/OpenAI), có thể đưa thêm `chunks` để “RAG-assist”.
- **Interview Generator**: sinh câu hỏi theo tỉ lệ `technical / behavioral / situational`, đa ngôn ngữ (vi/en), có rubric đánh giá.
- **Versioning**: lưu mọi lần chỉnh sửa, có `version-history`, `change_summary`, rollback/audit.
- **RAG Retriever (Milvus, cosine)**: tìm nhanh các đoạn JD tương tự (snippet + metadata), không cần đọc file gốc.
- **Export**: xuất **PDF/DOCX** từ Markdown.

---

## 2) Cấu trúc thư mục
```
JD_CV_Enhancement/
├── src/
│   ├── main.py
│   ├── api/
│   │   ├── auth/            # /auth/token, /auth/me
│   │   └── v1/              # /v1/jd, /v1/interview, /v1/retrieve, /v1/roles
│   ├── services/            # orchestrator, versioning, retriever, access control...
│   ├── crud/                # SQLAlchemy CRUD
│   ├── db/                  # models, session, base
│   ├── schemas/             # Pydantic models (auth, jd, interview, roles)
│   ├── utils/               # export PDF/DOCX, file_extract
│   └── core/                # config.py (ENV)
├── etl/
│   ├── jd_markdown/         # JD mẫu (.md) - LƯU LOCAL
│   └── jd_etl.py            # Parse JD .md → DB (schema `smarthire`)
├── embeddings/
│   ├── utils/
│   │   ├── gemini_embed.py  # Embed query/chunk qua Gemini (hoặc fallback local)
│   │   └── chunker.py       # Chunk markdown
│   ├── jd_chunk_embed.py    # Chunk + embed + upsert Milvus
│   └── chunk_utils.py       # Tiện ích embed/format
├── infra/
│   └── migrations/          # SQL tạo schema, tables, seed
├── frontend/                # React + Tailwind (UI)
├── requirements.txt
└── README.md
```

---

## 3) Yêu cầu hệ thống
- **Python** ≥ 3.12
- **PostgreSQL** trên **AWS RDS** (đã có DB + user)
- **Milvus** chạy trên **EC2** (standalone), mở port 19530
- (Tùy chọn) **Node 18+** nếu build frontend

---

## 4) Cấu hình môi trường
Tạo file `.env` ở gốc repo:

```env
# --- DB (AWS RDS) ---
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432
DB_NAME=hcm
DB_USER=quannguyen
DB_PASS=***your-password***
DB_SCHEMA=smarthire

# --- JWT ---
JWT_SECRET_KEY=***your-secret***
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- LLM / Embedding ---
GEMINI_API_KEY=***your-gemini-key***
GEMINI_CHAT_MODEL=gemini-2.0-flash-exp
GEMINI_EMBED_MODEL=text-embedding-004
EMBEDDING_MODEL=all-MiniLM-L6-v2  # fallback local nếu thiếu Gemini

# --- Milvus ---
MILVUS_HOST=10.0.1.136
MILVUS_PORT=19530
MILVUS_COLLECTION=jdchunks
VECTOR_DIM=768
```

> Dự án **không dùng MinIO/S3** trong bản này: JD mẫu & chunk giữ ở **local**.

---

## 5) Cài đặt & chạy Backend
```bash
# 1) Tạo venv & cài dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pip install "pydantic[email]" passlib[bcrypt]

# 2) (EC2) Export PYTHONPATH nếu cần
export PYTHONPATH=$(pwd)

# 3) Chạy API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
Mở **Swagger**: `http://<EC2_IP>:8000/docs`

---

## 6) Khởi tạo DB (migrations)
Dùng các file SQL trong `infra/migrations/`. Ví dụ với `psql`:

```bash
# Set search_path sang schema riêng
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER" -c "SET search_path TO ${DB_SCHEMA}, public;"

# Chạy lần lượt các file (ví dụ)
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER" -f infra/migrations/010_roles.sql
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER" -f infra/migrations/020_users.sql
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER" -f infra/migrations/030_job_families.sql
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER" -f infra/migrations/040_job_descriptions.sql
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER" -f infra/migrations/050_jd_versions.sql
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER" -f infra/migrations/060_tags.sql
```

**Seed ví dụ**:
```sql
-- Chạy sau khi SET search_path TO smarthire, public;
INSERT INTO roles (role_name) VALUES ('admin') ON CONFLICT DO NOTHING;
INSERT INTO roles (role_name) VALUES ('recruiter') ON CONFLICT DO NOTHING;

INSERT INTO users (username, full_name, email, hashed_pw, is_active)
VALUES ('alice', 'Alice HR', 'alice@example.com', '$2b$12$abcdefghijklmnopqrstuv', true)
ON CONFLICT (username) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.user_id, r.role_id FROM users u, roles r
WHERE u.username='alice' AND r.role_name='admin'
ON CONFLICT DO NOTHING;
```

---

## 7) Kiểm tra kết nối RDS & Milvus
**RDS**
```bash
python - <<'PY'
import os, psycopg2
dsn = f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASS')}"
with psycopg2.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_schema()")
        print(cur.fetchone())
PY
```

**Milvus**
```bash
python - <<'PY'
import os
from pymilvus import connections, list_collections, utility
connections.connect(host=os.getenv("MILVUS_HOST"), port=os.getenv("MILVUS_PORT"))
print("Collections:", list_collections())
print("Has jdchunks:", utility.has_collection(os.getenv("MILVUS_COLLECTION")))
PY
```

---

## 8) ETL JD mẫu & Embeddings
1) Đặt JD `.md` vào: `etl/jd_markdown/`

2) ETL → DB
```bash
python etl/jd_etl.py \
  --root-dir etl/jd_markdown \
  --schema $DB_SCHEMA
```

3) Chunk + Embed + Upsert Milvus
```bash
python embeddings/jd_chunk_embed.py \
  --root-dir etl/jd_markdown \
  --collection $MILVUS_COLLECTION \
  --dim $VECTOR_DIM \
  --normalize
```
> Embedding dùng **Gemini** (`GEMINI_API_KEY`). Nếu thiếu, mã sẽ dùng **EMBEDDING_MODEL** local (sentence-transformers) nếu đã cài.

---

## 9) API chính (mẫu payload)
### Auth
- `POST /auth/token` → lấy JWT (form: `username`, `password`)
- `GET /auth/me` → thông tin user hiện tại

### JD
- `POST /v1/jd/generate`
```json
{
  "title": "Data Engineer",
  "level": "Senior",
  "department": "Data",
  "job_family": "Data Platform",
  "chunks": [
    "We operate pipelines on Airflow + Spark (AWS EMR)…",
    "Must follow security and encryption best practices…"
  ]
}
```
Phản hồi:
```json
{ "jd_id": 123, "content_md": "## Data Engineer (Senior)...", "version": 1 }
```

- `PUT /v1/jd/update`
```json
{ "jd_id": 123, "content_md": "## Data Engineer (Senior)\n...", "change_summary": "Refine responsibilities" }
```

- `GET /v1/jd/version-history/{jd_id}` → danh sách phiên bản
- `GET /v1/jd/export/{jd_id}?format=pdf|docx` → bytes file

### Interview
- `POST /v1/interview/generate`
```json
{
  "jd_id": 123,
  "title": "Data Engineer",
  "level": "Senior",
  "department": "Data",
  "focus": ["spark", "airflow", "aws"],
  "count": 8,
  "mix": ["technical", "behavioral", "situational"],
  "language": "vi"
}
```

### Retrieve (RAG - Milvus)
- `POST /v1/retrieve/similar`
```json
{ "query": "Airflow Spark on AWS EMR with data encryption", "top_k": 5 }
```
Kết quả gồm `chunk_id`, `jd_id`, `chunk_index`, `object_path` (đường dẫn local tệp chunk), `score` (cosine) + **snippet** tóm tắt nội dung đoạn.

---

## 10) Troubleshooting
- **`Fail connecting to server on MILVUS_HOST:19530`** → Kiểm tra Security Group EC2, inbound port 19530.
- **`field object_path not exist`** khi search → Chạy lại script `jd_chunk_embed.py` để tạo collection với schema đúng cột.
- **Unicode/encoding khi export** → Bảo đảm JD Markdown UTF-8, tránh smart-quotes.
- **Pydantic/JWT lỗi serialize user** → `schemas/auth.py` bật `orm_mode` và map `roles: List[str]` từ `Role.role_name`.

---

## 11) Triển khai EC2 nhanh
- Pull repo & tạo `.env`
- Cài đặt venv + requirements
- Chạy API: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
- Milvus chạy cùng/khác EC2; RDS mở 5432 cho EC2
- (Khuyên dùng) Nginx reverse proxy + systemd service để chạy nền

---

## License
Private / Internal (CMCC). Không công khai nếu chưa được phép.
