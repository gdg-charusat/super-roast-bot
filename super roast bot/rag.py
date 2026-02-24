"""
RAG (Retrieval-Augmented Generation) module for RoastBot.
Loads roast data, chunks it, embeds it, and retrieves relevant
context for each user query using FAISS.
"""
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader # New import

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def get_text_from_files():
    """Reads all .txt and .pdf files from the data folder."""
    all_text = ""
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        
        # Handle Text Files
        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f.read() + "\n"
        
        # Handle PDF Files
        elif filename.endswith(".pdf"):
            reader = PdfReader(file_path)
            for page in reader.pages:
                all_text += page.extract_text() + "\n"
                
    return all_text

def load_and_chunk(chunk_size: int = 500) -> list[str]:
    """Chunks text retrieved from multiple files."""
    text = get_text_from_files()
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



CHUNKS = load_and_chunk()
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

   

    # Pre-load data and index at startup



    query_embedding = EMBEDDING_MODEL.encode([query])
    distances, indices = INDEX.search(
        np.array(query_embedding).astype("float32"), top_k
    )

    results = [CHUNKS[i] for i in indices[0] if i < len(CHUNKS)]
    return "\n\n".join(results)
