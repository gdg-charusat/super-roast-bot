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
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def load_and_chunk(file_path: str, chunk_size: int = 500) -> list[str]: 
    """
    Load a text file and split it into chunks.

    Args:
        file_path: Path to the text file.
        chunk_size: Number of characters per chunk.

    Returns:
        List of text chunks.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def build_index(chunks: list[str], embedding_model):
    """Build a FAISS index from text chunks."""
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
    return index



CHUNKS = load_and_chunk(DATA_PATH)
INDEX = build_index(CHUNKS,EMBEDDING_MODEL)

def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant roast context for a user query.

    Args:
        query: The user's message.
        top_k: Number of top results to return.

    Returns:
        Concatenated relevant text chunks.
    """
    query_embedding = EMBEDDING_MODEL.encode([query])
    distances, indices = INDEX.search(
        np.array(query_embedding).astype("float32"), top_k
    )

    results = [CHUNKS[i] for i in indices[0] if i < len(CHUNKS)]
    return "\n\n".join(results)
