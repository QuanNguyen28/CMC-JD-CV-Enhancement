# src/services/retriever_service.py
from typing import List, Dict, Any
from embeddings.chunk_utils import chunk_text
from embeddings.utils.gemini_embed import embed_text
from src.crud.version_crud import get_all_chunks
import numpy as np

class RetrieverService:
    @staticmethod
    def retrieve_similar(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Return top_k most similar chunks to the query.
        """
        # Chunk the query
        chunks = chunk_text(query)
        # Embed each chunk
        query_vecs = embed_text(chunks)
        # Load stored chunks with their embeddings
        stored = get_all_chunks()
        results = []
        for qv in query_vecs:
            for item in stored:
                # Cosine similarity
                score = np.dot(qv, item['vector']) / (np.linalg.norm(qv) * np.linalg.norm(item['vector']))
                results.append({"chunk": item['text'], "score": float(score)})
        # Sort and slice
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]