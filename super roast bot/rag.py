import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader 

# Use the data folder instead of a single file
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def get_text_from_files():
    """Reads all .txt and .pdf files from the data folder."""
    all_text = ""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER) # Create folder if it doesn't exist
        return "No data found."
        
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        
        # Process Text Files
        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f.read() + "\n"
        
        # Process PDF Files
        elif filename.endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        all_text += content + "\n"
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")
                
    return all_text

def load_and_chunk(chunk_size: int = 500) -> list[str]:
    """Retrieves combined text and splits into chunks for FAISS."""
    text = get_text_from_files()
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def build_index(chunks: list[str], embedding_model):
    """Build a FAISS index from text chunks."""
    if not chunks:
        # Fallback if data folder is empty
        chunks = ["Default roast: Your code is so dry it's a fire hazard."]
        
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
    return index, chunks

# Build index at startup
ALL_CHUNKS, PROCESSED_CHUNKS = load_and_chunk(), []
INDEX, CHUNKS = build_index(ALL_CHUNKS, EMBEDDING_MODEL)

def retrieve_context(query: str, top_k: int = 3) -> str:
    """Retrieve relevant context using the corrected FAISS index."""
    query_embedding = EMBEDDING_MODEL.encode([query])
    distances, indices = INDEX.search(
        np.array(query_embedding).astype("float32"), top_k
    )
    # Fixed: Use indices[0] for correct result mapping
    results = [CHUNKS[i] for i in indices[0] if i < len(CHUNKS)]
    return "\n\n".join(results)