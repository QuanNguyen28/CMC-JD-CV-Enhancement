#!/usr/bin/env python
"""
retriever/app.py

FastAPI semantic retriever using Milvus for vector search and Gemini for query embeddings.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sys

# Add the parent directory to the path to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pymilvus import connections, Collection
from utils.gemini_embed import embed_text  

load_dotenv()

MILVUS_HOST       = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT       = os.getenv("MILVUS_PORT", "19530")
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "jdchunks")

# Connect to Milvus
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
collection = Collection(MILVUS_COLLECTION)

# Load collection into memory for search operations
collection.load()

app = FastAPI(title="JD Retriever")

class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5

class ChunkResult(BaseModel):
    chunk_id: str
    jd_id: int
    chunk_index: int
    object_url: str
    score: float

@app.post("/retrieve", response_model=list[ChunkResult])
def retrieve(req: RetrieveRequest):
    try:
        # Embed the query using Gemini
        print(f"Embedding query: {req.query}")
        query_embeddings = embed_text([req.query])
        query_vector = query_embeddings[0]
        
        print(f"Query vector dimension: {len(query_vector)}")
        
        # Search in Milvus using COSINE similarity
        search_params = {
            "metric_type": "COSINE",  # Use COSINE similarity for text embeddings
            "params": {"nprobe": 50}
        }
        
        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=req.top_k,
            output_fields=["chunk_id", "jd_id", "chunk_index", "object_url"]
        )
        
        hits = results[0]
        print(f"Found {len(hits)} results")

        if not hits:
            raise HTTPException(status_code=404, detail="No matches found")

        # Format results
        out = []
        for hit in hits:
            out.append(ChunkResult(
                chunk_id=hit.entity.get("chunk_id"),        
                jd_id=hit.entity.get("jd_id"),
                chunk_index=hit.entity.get("chunk_index"),
                object_url=hit.entity.get("object_url"),
                score=hit.score  # Milvus returns similarity score
            ))
        
        return out
        
    except Exception as e:
        print(f"Error during retrieval: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@app.get("/ping")
def ping():
    return {"status": "ok", "collection": MILVUS_COLLECTION, "entities": collection.num_entities}

@app.get("/health")
def health():
    """Health check endpoint that verifies Milvus connection and collection status"""
    try:
        # Check if collection is loaded
        collection.load()
        entity_count = collection.num_entities
        return {
            "status": "healthy",
            "milvus_connected": True,
            "collection_name": MILVUS_COLLECTION,
            "total_entities": entity_count,
            "collection_loaded": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "milvus_connected": False,
            "collection_name": MILVUS_COLLECTION
        }
