# embeddings/schema.py
from __future__ import annotations
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection, utility
)

from src.core.config import MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION, VECTOR_DIM

COLLECTION_NAME   = MILVUS_COLLECTION
FIELD_CHUNK_ID    = "chunk_id"
FIELD_JD_ID       = "jd_id"
FIELD_INDEX       = "chunk_index"
FIELD_OBJECT_URL  = "object_url"
FIELD_EMBEDDING   = "embedding"

_DEFAULT_INDEX = {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {"M": 32, "efConstruction": 200},
}

def connect() -> None:
    connections.connect(alias="default", host=MILVUS_HOST, port=str(MILVUS_PORT))

def _schema() -> CollectionSchema:
    fields = [
        FieldSchema(name=FIELD_CHUNK_ID,   dtype=DataType.VARCHAR, max_length=64,   is_primary=True),
        FieldSchema(name=FIELD_JD_ID,      dtype=DataType.INT64),
        FieldSchema(name=FIELD_INDEX,      dtype=DataType.INT64),
        FieldSchema(name=FIELD_OBJECT_URL, dtype=DataType.VARCHAR, max_length=1024),
        FieldSchema(name=FIELD_EMBEDDING,  dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
    ]
    return CollectionSchema(fields, description="JD chunks for semantic search (COSINE)")

def ensure_collection(index_params: Optional[dict] = None, *, load: bool = True) -> Collection:
    index_params = index_params or _DEFAULT_INDEX
    if not utility.has_collection(COLLECTION_NAME):
        col = Collection(COLLECTION_NAME, _schema(), consistency_level="Strong")
        col.create_index(field_name=FIELD_EMBEDDING, index_params=index_params)
    else:
        col = Collection(COLLECTION_NAME)
    if load:
        try:
            col.load()
        except Exception:
            pass
    return col

def drop_collection() -> None:
    if utility.has_collection(COLLECTION_NAME):
        utility.drop_collection(COLLECTION_NAME)