#!/usr/bin/env bash
# scripts/run_demo.sh
# Demo orchestration: migrations → ETL → embedding → start APIs → start frontend

set -e

echo "⏳ Waiting for PostgreSQL, MinIO, Milvus to be ready..."
# simple wait; adjust as needed
sleep 10

# 1. Run migrations
echo "🏗️  Applying database migrations..."
psql "postgresql://hoangquannguyen:mypassword@localhost:5432/jd_library" \
  -f infra/migrations/001_create_candidate_profiles.sql \
  -f infra/migrations/002_create_job_descriptions.sql \
  -f infra/migrations/003_create_jd_versions.sql

# 2. ETL JD & Profiles
echo "🚚 Running ETL for Job Descriptions..."
python api/etl/jd_etl.py

echo "🚚 Running ETL for Candidate Profiles..."
python api/etl/profiles_etl.py

# 3. Chunk & Embed JDs
echo "🤖 Chunking & embedding Job Descriptions..."
python api/embeddings/jd_chunk_embed.py

# 4. Start backend services
echo "🚀 Starting Retriever service on port 8000..."
uvicorn api/retriever/app:app --host 0.0.0.0 --port 8000 --reload &
PID_RETRIEVER=$!

echo "🚀 Starting Prompt Generator service on port 9000..."
uvicorn api/prompt_generator/app:app --host 0.0.0.0 --port 9000 --reload &
PID_PROMPT=$!

# 5. Start frontend
echo "📦 Starting React frontend..."
(
  cd frontend
  npm install --silent
  npm run dev
) &

# Wait for any background service to exit
wait -n
echo "⚠️ One of the demo services has exited. Shutting down."
kill $PID_RETRIEVER $PID_PROMPT 2>/dev/null || true
