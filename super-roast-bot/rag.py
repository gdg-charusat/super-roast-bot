"""
RAG (Retrieval-Augmented Generation) module for RoastBot.
Loads roast data, chunks it, embeds it, and retrieves relevant
context for each user query using FAISS.
"""
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "roast_data.txt")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Lazy-loaded globals (init on first use)
_embedding_model = None
_chunks = None
_index = None


def _get_embedding_model():
    """Lazy-load embedding model on first use.

    This wraps the heavyweight `SentenceTransformer` import so importing this
    module doesn't crash on systems without that dependency. If the model
    cannot be imported, we return `None` and callers should handle graceful
    fallback.
    """
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        except Exception as e:
            # Model not available (environment may not have sentence-transformers)
            print(f"SentenceTransformer not available: {e}")
            _embedding_model = None
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

    # Attempt to import FAISS and numpy locally so module import doesn't fail
    try:
        import numpy as np
        import faiss
    except Exception as e:
        print(f"FAISS or numpy not available: {e}. Returning empty index.")
        empty_embeddings = None
        try:
            # fallback: create a minimal numpy-like array shape if numpy available
            import numpy as _np

            empty_embeddings = _np.zeros((1, 384)).astype("float32")
            index = None
            try:
                import faiss as _faiss

                index = _faiss.IndexFlatL2(384)
                index.add(empty_embeddings)
            except Exception:
                index = None
        except Exception:
            index = None
        return chunks, index

    if not chunks:
        print("Warning: No chunks to index. Creating empty index.")
        empty_embeddings = np.zeros((1, 384)).astype("float32")
        index = faiss.IndexFlatL2(384)
        index.add(empty_embeddings)
        return chunks, index

    if embedding_model is None:
        embedding_model = _get_embedding_model()

    if embedding_model is None:
        # Embedding model not available; return empty/placeholder index
        print("Embedding model not available; returning empty index.")
        empty_embeddings = np.zeros((1, 384)).astype("float32")
        index = faiss.IndexFlatL2(384)
        index.add(empty_embeddings)
        return chunks, index

    try:
        embeddings = embedding_model.encode(chunks, batch_size=32)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings).astype("float32"))
        return chunks, index
    except Exception as e:
        print(f"Error building FAISS index: {e}. Returning empty index.")
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

        if not chunks or index is None or (hasattr(index, "ntotal") and index.ntotal == 0):
            return "No roast context available. I'll roast from pure instinct."

        query_embedding = embedding_model.encode([query])
        import numpy as np

        distances, indices = index.search(
            np.array(query_embedding).astype("float32"), 
            min(top_k, len(chunks))
        )

        results = [chunks[i] for i in indices[0] if i < len(chunks) and i >= 0]
        return "\n\n".join(results) if results else "No roast context found."

    except Exception as e:
        print(f"Error during retrieval: {e}")
        return "No roast context available. I'll roast from pure instinct."
import os
import faiss
import numpy as np
import threading
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader 

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

# Thread-safe singleton for RAG components
_rag_lock = threading.Lock()
_rag_initialized = False
_global_chunks = None
_global_index = None
_global_model = None

def get_text_from_files():
    all_text = ""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return ""
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f.read() + "\n"
        elif filename.endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    content = page.extract_text()
                    if content: # SAFETY FIX FOR NONE-TYPE
                        all_text += str(content).strip() + "\n"
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return all_text

def load_and_chunk(chunk_size=500):
    text = get_text_from_files()
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size) if text[i:i+chunk_size].strip()]
    return chunks or ["No data"]

def build_index(chunks, model):
    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
    return index, chunks

def _initialize_rag_components():
    """Thread-safe lazy initialization of RAG components."""
    global _rag_initialized, _global_chunks, _global_index, _global_model
    
    if not _rag_initialized:
        with _rag_lock:
            if not _rag_initialized:  # Double-check locking
                _global_model = SentenceTransformer("all-MiniLM-L6-v2")
                chunks_list = load_and_chunk()
                _global_index, _global_chunks = build_index(chunks_list, _global_model)
                _rag_initialized = True

def retrieve_context(query, top_k=3):
    """Thread-safe context retrieval - lock only for encoding."""
    _initialize_rag_components()
    
    # Encode with lock, search without (FAISS reads are thread-safe)
    with _rag_lock:
        query_embedding = _global_model.encode([query])
    
    _, indices = _global_index.search(np.array(query_embedding).astype("float32"), top_k)
    return "\n\n".join([_global_chunks[i] for i in indices[0] if i < len(_global_chunks)])