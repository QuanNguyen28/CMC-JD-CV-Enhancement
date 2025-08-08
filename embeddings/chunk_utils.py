"""
embeddings/chunk_utils.py

Utility functions for splitting text into manageable chunks.
"""
from typing import List


def chunk_text(text: str, max_words: int = 300) -> List[str]:
    """
    Split text into chunks up to `max_words` words, preserving paragraph boundaries.
    Long paragraphs are further split by word count.
    """
    def split_para(para_words):
        # Generator: yields slices of para_words of size max_words
        for i in range(0, len(para_words), max_words):
            yield para_words[i:i + max_words]

    paragraphs = text.split("\n\n")
    chunks = []
    current = []
    current_count = 0

    for para in paragraphs:
        words = para.split()
        if len(words) > max_words:
            # flush existing
            if current:
                chunks.append("\n\n".join(current).strip())
                current, current_count = [], 0
            # split and append long paragraph parts
            for part in split_para(words):
                chunks.append(" ".join(part).strip())
        elif current_count + len(words) <= max_words:
            current.append(para)
            current_count += len(words)
        else:
            # flush and start new chunk
            chunks.append("\n\n".join(current).strip())
            current = [para]
            current_count = len(words)

    if current:
        chunks.append("\n\n".join(current).strip())

    return chunks
