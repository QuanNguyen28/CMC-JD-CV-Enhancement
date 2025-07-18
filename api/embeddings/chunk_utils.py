"""
embeddings/chunk_utils.py

Utility functions for splitting text into manageable chunks.
"""
from typing import List


def chunk_text(text: str, max_words: int = 300) -> List[str]:
    """
    Split the given text into chunks of up to `max_words` words, preserving paragraph boundaries.

    Args:
        text: The full text to chunk (e.g., a job description in Markdown).
        max_words: Maximum number of words per chunk.

    Returns:
        A list of text chunks.
    """
    # Split by double newlines to respect paragraphs
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current_chunk = []
    current_word_count = 0

    for para in paragraphs:
        words = para.split()
        if current_word_count + len(words) <= max_words:
            # Add paragraph to current chunk
            current_chunk.append(para)
            current_word_count += len(words)
        else:
            # Flush current chunk
            if current_chunk:
                chunks.append("\n\n".join(current_chunk).strip())
            # Start new chunk(s)
            if len(words) > max_words:
                # If a single paragraph is too long, split it by words
                for i in range(0, len(words), max_words):
                    part = words[i : i + max_words]
                    chunks.append(" ".join(part).strip())
                current_chunk = []
                current_word_count = 0
            else:
                current_chunk = [para]
                current_word_count = len(words)

    # Append the final chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk).strip())

    return chunks
