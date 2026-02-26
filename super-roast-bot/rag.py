import os
import faiss
import numpy as np
import threading
import time
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader 

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_TEXT_CHARS = 200_000
MAX_PDF_PAGES = 80

_MODEL = None
_INDEX = None
_CHUNKS = None
_INIT_LOCK = threading.Lock()

_CONTEXT_CACHE = {}
_CACHE_LOCK = threading.Lock()
_CACHE_TTL_SECONDS = 300
_MAX_CACHE_ITEMS = 256


def _sanitize_text(text: str) -> str:
    cleaned = text.replace("\x00", "")
    cleaned = "".join(ch for ch in cleaned if ch.isprintable() or ch in "\n\t")
    return cleaned.strip()

def get_text_from_files():
    all_text = ""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return ""
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        if not os.path.isfile(file_path):
            continue
        if not (filename.endswith(".txt") or filename.endswith(".pdf")):
            continue
        if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
            continue

        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                all_text += _sanitize_text(f.read()) + "\n"
        elif filename.endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                for page in reader.pages[:MAX_PDF_PAGES]:
                    content = page.extract_text()
                    if content: # SAFETY FIX FOR NONE-TYPE
                        all_text += _sanitize_text(str(content)) + "\n"
            except Exception as e:
                print(f"Error reading {filename}: {e}")

        if len(all_text) >= MAX_TOTAL_TEXT_CHARS:
            return all_text[:MAX_TOTAL_TEXT_CHARS]
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

def _ensure_initialized():
    global _MODEL, _INDEX, _CHUNKS
    if _MODEL is not None and _INDEX is not None and _CHUNKS is not None:
        return

    with _INIT_LOCK:
        if _MODEL is not None and _INDEX is not None and _CHUNKS is not None:
            return
        model = SentenceTransformer("all-MiniLM-L6-v2", token=False)
        chunks_list = load_and_chunk()
        index, chunks = build_index(chunks_list, model)
        _MODEL = model
        _INDEX = index
        _CHUNKS = chunks


def _normalize_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def _prune_cache_if_needed(now_ts: float):
    expired_keys = [key for key, (_, expiry) in _CONTEXT_CACHE.items() if expiry <= now_ts]
    for key in expired_keys:
        _CONTEXT_CACHE.pop(key, None)

    if len(_CONTEXT_CACHE) > _MAX_CACHE_ITEMS:
        oldest = sorted(_CONTEXT_CACHE.items(), key=lambda item: item[1][1])
        for key, _ in oldest[: len(_CONTEXT_CACHE) - _MAX_CACHE_ITEMS]:
            _CONTEXT_CACHE.pop(key, None)

def retrieve_context(query, top_k=3):
    _ensure_initialized()
    normalized_query = _normalize_query(query)
    cache_key = (normalized_query, int(top_k))
    now_ts = time.time()

    with _CACHE_LOCK:
        cached = _CONTEXT_CACHE.get(cache_key)
        if cached and cached[1] > now_ts:
            return cached[0]
        _prune_cache_if_needed(now_ts)

    query_embedding = _MODEL.encode([query])
    _, indices = _INDEX.search(np.array(query_embedding).astype("float32"), top_k)
    context = "\n\n".join([_CHUNKS[i] for i in indices[0] if i < len(_CHUNKS)])

    with _CACHE_LOCK:
        _CONTEXT_CACHE[cache_key] = (context, now_ts + _CACHE_TTL_SECONDS)

    return context