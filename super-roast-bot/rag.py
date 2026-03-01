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