import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader 

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def get_text_from_files():
    all_text = ""
    if not os.path.exists(DATA_FOLDER):
        return "No data found."
        
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f.read() + "\n"
        elif filename.endswith(".pdf"):
            reader = PdfReader(file_path)
            for page in reader.pages:
                all_text += (page.extract_text() or "") + "\n"
    return all_text

def load_and_chunk(chunk_size: int = 500) -> list[str]:
    text = get_text_from_files()
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def build_index(chunks: list[str], embedding_model):
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
    return index

CHUNKS = load_and_chunk()
INDEX = build_index(CHUNKS, EMBEDDING_MODEL)

def retrieve_context(query: str, top_k: int = 3) -> str:
    query_embedding = EMBEDDING_MODEL.encode([query])
    distances, indices = INDEX.search(
        np.array(query_embedding).astype("float32"), top_k
    )
    # Fixed from indices[1] to indices[0]
    results = [CHUNKS[i] for i in indices[0] if i < len(CHUNKS)]
    return "\n\n".join(results)