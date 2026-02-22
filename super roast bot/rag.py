"""
RAG (Retrieval-Augmented Generation) module for RoastBot.
Loads roast data, chunks it, embeds it, and retrieves relevant
context for each user query using FAISS.
"""

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "roast_data.txt")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Lazy-loaded globals (init on first use)
_embedding_model = None
_chunks = None
_index = None


def _get_embedding_model():
    """Lazy-load embedding model on first use."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _get_index():
    """Lazy-load chunks and FAISS index on first use."""
    global _chunks, _index
    if _chunks is None or _index is None:
        _chunks, _index = _build_index()
    return _chunks, _index


def load_and_chunk(file_path: str, chunk_size: int = 300) -> list[str]:
    """
    Load a text file and split it into semantic chunks.

    Args:
        file_path: Path to the text file.
        chunk_size: Approximate number of characters per chunk (default 300).

    Returns:
        List of text chunks, split on sentence/line boundaries when possible.
    """
    if not os.path.exists(file_path):
        print(f"Warning: Data file not found at {file_path}. Returning empty chunks.")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    current_chunk = ""

    # Split on sentences/newlines and recombine to maintain ~chunk_size
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            continue

        # Add line to current chunk; if it exceeds chunk_size, start a new one
        if len(current_chunk) + len(line) + 1 > chunk_size and current_chunk.strip():
            chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += (" " + line if current_chunk else line)

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _build_index(chunks: list[str] = None, embedding_model=None) -> tuple:
    """Build a FAISS index from text chunks."""
    if chunks is None:
        chunks = load_and_chunk(DATA_PATH)
    
    if not chunks:
        print("Warning: No chunks to index. Creating empty index.")
        # Return empty index for graceful fallback
        empty_embeddings = np.zeros((1, 384)).astype("float32")  # MiniLM-L6-v2 has 384 dims
        index = faiss.IndexFlatL2(384)
        index.add(empty_embeddings)
        return chunks, index

    if embedding_model is None:
        embedding_model = _get_embedding_model()

    try:
        embeddings = embedding_model.encode(chunks, batch_size=32)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings).astype("float32"))
        return chunks, index
    except Exception as e:
        print(f"Error building FAISS index: {e}. Returning empty index.")
        # Graceful fallback
        chunks = []
        empty_embeddings = np.zeros((1, 384)).astype("float32")
        index = faiss.IndexFlatL2(384)
        index.add(empty_embeddings)
        return chunks, index


def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant roast context for a user query.

    Args:
        query: The user's message.
        top_k: Number of top results to return.

    Returns:
        Concatenated relevant text chunks, or a default message if none found.
    """
    try:
        chunks, index = _get_index()
        embedding_model = _get_embedding_model()

        if not chunks or index.ntotal == 0:
            return "No roast context available. I'll roast from pure instinct."

        query_embedding = embedding_model.encode([query])
        distances, indices = index.search(
            np.array(query_embedding).astype("float32"), 
            min(top_k, len(chunks))
        )

        results = [chunks[i] for i in indices[0] if i < len(chunks) and i >= 0]
        return "\n\n".join(results) if results else "No roast context found."

    except Exception as e:
        print(f"Error during retrieval: {e}")
        return "No roast context available. I'll roast from pure instinct."

