#!/usr/bin/env python
"""
embeddings/jd_chunk_embed.py

Chunk Job Descriptions, embed via Gemini REST, upload chunk text to MinIO,
and store embeddings + metadata in Milvus.
"""

import os
import time
import psycopg2
from minio import Minio
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from tqdm import tqdm
import io

from src.core.config import DATABASE_URL, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION, VECTOR_DIM

from utils.gemini_embed import embed_text  


print(f"INFO: Using vector dimension: {VECTOR_DIM}")


# Connect MinIO
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

# Connect Milvus with retry logic
print("Connecting to Milvus...")
for i in range(30):  # thử 30 lần, mỗi lần cách nhau 2s
    try:
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        print("✅ Milvus connected!")
        break
    except Exception as e:
        print(f"Waiting for Milvus to be ready... ({i+1}/30)")
        time.sleep(2)
else:
    raise RuntimeError("Milvus is not ready after waiting.")

# Define schema
fields = [
    FieldSchema(name="chunk_id",    dtype=DataType.VARCHAR,     is_primary=True, max_length=64),
    FieldSchema(name="embedding",   dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
    FieldSchema(name="jd_id",       dtype=DataType.INT64),
    FieldSchema(name="chunk_index", dtype=DataType.INT64),
    FieldSchema(name="object_url",  dtype=DataType.VARCHAR,     max_length=512), 
]
schema = CollectionSchema(fields, description="JD chunks with embeddings")

if utility.has_collection(MILVUS_COLLECTION):
    print(f"Dropping existing collection '{MILVUS_COLLECTION}' to ensure clean state...")
    utility.drop_collection(MILVUS_COLLECTION)

print(f"INFO: Creating collection '{MILVUS_COLLECTION}' with schema...")
collection = Collection(name=MILVUS_COLLECTION, schema=schema)

# Create index with COSINE similarity for better text embedding search
index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}
print("Creating COSINE similarity index on embedding field...")
collection.create_index(field_name="embedding", index_params=index_params)
print("✅ Index created successfully")


# Connect PostgreSQL
psql_conn = psycopg2.connect(DATABASE_URL)
psql_cur = psql_conn.cursor()

def chunk_text(text: str, max_words: int = 300) -> list[str]:
    paras, chunks, current = text.split("\n\n"), [], ""
    for p in paras:
        words = (current + " " + p).split()
        if len(words) <= max_words:
            current = (current + "\n\n" + p).strip()
        else:
            if current:
                chunks.append(current.strip())
            current = p
    if current:
        chunks.append(current.strip())
    return chunks

# Process JDs
psql_cur.execute("SELECT jd_id, content_md FROM job_descriptions;")
total_inserted_count = 0
for jd_id, content in tqdm(psql_cur.fetchall(), desc="Embedding JDs"):
    chunks = chunk_text(content)
    if not chunks:
        continue
        
    embeddings = embed_text(chunks)  # Gemini SDK
    chunk_ids, vecs, jd_ids, idxs, urls = [], [], [], [], []
    for idx, (chunk, vec) in enumerate(zip(chunks, embeddings)):
        cid = f"{jd_id}_{idx}"
        obj = f"jd_{jd_id}_chunk_{idx}.txt"
        data = chunk.encode("utf-8")
        try:
            minio_client.put_object(
                MINIO_BUCKET, 
                obj, 
                io.BytesIO(data), 
                len(data),
                content_type="text/plain"
            )
            url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{obj}"

            chunk_ids.append(cid)
            vecs.append(vec)
            jd_ids.append(jd_id)
            idxs.append(idx)
            urls.append(url)
        except Exception as minio_err:
            print(f"❌ Failed to upload chunk {cid} to MinIO: {minio_err}")


    if chunk_ids: 
        insert_result = collection.insert([chunk_ids, vecs, jd_ids, idxs, urls])
        collection.flush() # Ensure data is written to disk
        inserted_count = insert_result.insert_count
        total_inserted_count += inserted_count
        # print(f"INFO: Flushed {inserted_count} new entities to Milvus for JD {jd_id}.")


psql_cur.close()
psql_conn.close()
print(f"✅ Completed chunking & embedding. Total new entities flushed to Milvus: {total_inserted_count}.")