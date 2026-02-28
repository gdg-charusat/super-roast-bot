"""
RAG Retrieval — rag.py (Theme-Aware Edition)

Changes from original:
  • load_and_chunk() strips [THEME:xxx] tags from text before embedding
    but records each chunk's theme in a parallel CHUNK_THEMES list.
  • retrieve_context() gains an optional `dominant_theme` parameter.
    When supplied, semantically-matched chunks whose theme matches
    dominant_theme are bubbled to the top of the results.
  • All existing call signatures are fully backward-compatible.
"""

import os
import re

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

try:
    from PyPDF2 import PdfReader
    _PDF_SUPPORT = True
except ImportError:
    _PDF_SUPPORT = False

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# Regex that matches the optional [THEME:name] prefix on corpus lines
_THEME_TAG_RE = re.compile(r"^\[THEME:(\w+)\]\s*", re.IGNORECASE)


# ── Corpus loading ─────────────────────────────────────────────────────────────

def get_text_from_files() -> str:
    """Read all .txt and .pdf files from the data folder (unchanged behaviour)."""
    all_text = ""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return ""
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        if filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f.read() + "\n"
        elif filename.endswith(".pdf") and _PDF_SUPPORT:
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        all_text += str(content).strip() + "\n"
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return all_text


def load_and_chunk(chunk_size: int = 500):
    """
    Split corpus into chunks and extract per-chunk theme tags.

    Returns:
        chunks      : list[str]  — clean text (no [THEME:] prefix), used for embedding
        chunk_themes: list[str]  — parallel list of theme labels (or "" if untagged)
    """
    raw_text = get_text_from_files()

    # Try line-level theme extraction first (works when each line has its own tag)
    lines = [l.strip() for l in raw_text.splitlines() if l.strip() and not l.startswith("#")]

    chunks: list = []
    chunk_themes: list = []

    for line in lines:
        m = _THEME_TAG_RE.match(line)
        if m:
            theme = m.group(1).lower()
            text  = line[m.end():].strip()
        else:
            theme = ""
            text  = line

        if not text:
            continue

        # For long lines / paragraphs, sub-chunk at chunk_size characters
        for i in range(0, len(text), chunk_size):
            sub = text[i : i + chunk_size].strip()
            if sub:
                chunks.append(sub)
                chunk_themes.append(theme)

    if not chunks:
        return ["No data"], [""]

    return chunks, chunk_themes


def build_index(chunks, model):
    """Build a FAISS flat-L2 index from the chunk list."""
    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
    return index, chunks


# ── Module-level singletons (built once at import time) ────────────────────────

CHUNKS_LIST, CHUNK_THEMES = load_and_chunk()
INDEX, CHUNKS = build_index(CHUNKS_LIST, EMBEDDING_MODEL)


# ── Public API ─────────────────────────────────────────────────────────────────

def retrieve_context(query: str, top_k: int = 3, dominant_theme: str = "") -> str:
    """
    Retrieve the most relevant roast context for a user query.

    Args:
        query          : The user's message.
        top_k          : Number of chunks to return (default 3).
        dominant_theme : Optional theme name (e.g. "fitness", "career").
                         When supplied, chunks whose [THEME:] tag matches are
                         promoted to the front of the results so the LLM gets
                         theme-relevant roast material.
                         Pass "" or omit for pure semantic ranking (backward-compat).

    Returns:
        Newline-separated string of retrieved roast snippets.
    """
    query_embedding = EMBEDDING_MODEL.encode([query])

    # Fetch a wider candidate pool when we need to re-rank by theme
    fetch_k = top_k * 4 if dominant_theme else top_k
    fetch_k = min(fetch_k, len(CHUNKS))

    _, indices = INDEX.search(np.array(query_embedding).astype("float32"), fetch_k)
    candidate_indices = [i for i in indices[0] if i < len(CHUNKS)]

    if not dominant_theme:
        # Original behaviour: return top-k semantic matches as-is
        return "\n\n".join(CHUNKS[i] for i in candidate_indices[:top_k])

    # ── Theme-biased re-ranking ───────────────────────────────────────────────
    theme_norm = dominant_theme.lower().strip()
    themed   = [i for i in candidate_indices if CHUNK_THEMES[i] == theme_norm]
    unthemed = [i for i in candidate_indices if CHUNK_THEMES[i] != theme_norm]

    ranked = themed + unthemed
    selected = ranked[:top_k]

    return "\n\n".join(CHUNKS[i] for i in selected)