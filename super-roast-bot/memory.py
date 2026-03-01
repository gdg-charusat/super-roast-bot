import re
from database import add_chat_entry, get_chat_history, clear_chat_history

MAX_MEMORY = 10

def _sanitize(text: str) -> str:
    """
    Sanitize PII (Phone/Email) from chat messages.
    """
    if not text:
        return ""
    # Simple regex for demo/smoke test purposes
    # Replace email-like patterns
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL]', text)
    # Replace phone-like patterns (e.g., 555-123-4567)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    return text.strip()

def add_to_memory(user_msg: str, bot_msg: str, session_id: str = "default"):
    """
    Add a user-bot exchange to persistent memory (SQLite database).
    
    Args:
        user_msg: The user's message
        bot_msg: The bot's response
        session_id: Optional session identifier for multi-user support
    """
    # Persist to SQLite
    add_chat_entry(user_msg, bot_msg, session_id)

def get_memory(session_id: str = "default", limit: int = None) -> list:
    """
    Return current chat history as a list from the SQLite database.
    
    Args:
        session_id: Optional session identifier
        limit: Maximum number of entries to retrieve
    
    Returns:
        List of chat history entries
    """
    return get_chat_history(session_id, limit or MAX_MEMORY if MAX_MEMORY > 0 else None)

def clear_memory(session_id: str = "default"):
    """
    Clear all chat history for a session from the SQLite database.
    
    Args:
        session_id: The session whose history should be cleared
    """
    clear_chat_history(session_id)

def format_memory(session_id: str = "default") -> str:
    """
    Format chat history as a readable string for the LLM prompt.
    Retrieves from SQLite database for persistence.
    
    Args:
        session_id: Optional session identifier
    
    Returns:
        Formatted string of conversation history
    """
    # Get limited history for context (to avoid token overflow)
    history = get_memory(session_id, MAX_MEMORY if MAX_MEMORY > 0 else None)
    if not history:
        return "No previous conversation."
    return "\n\n".join(
        [f"User: {entry['user']}\nRoastBot: {entry['bot']}" for entry in history]
    )
"""
Adaptive Memory — memory.py

Stores chat history as importance-scored ScoredMessage objects.
High-scoring entries survive token trimming (handled by token_guard.py).

Backward-compatible: format_memory() still returns plain list[dict] so
app.py and token_guard.py need zero structural changes to existing call sites.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List

MAX_MEMORY = 20  # keep up to 20 message-pairs (40 individual messages)


@dataclass
class ScoredMessage:
    """A single chat message annotated with an importance score."""

    role: str          # "user" or "assistant"
    content: str
    importance: int = 1  # 0–10; higher → survives trimming

    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content}


# Module-level store — deque with a hard cap to prevent unbounded growth
_store: Deque[ScoredMessage] = deque(maxlen=MAX_MEMORY * 2)  # *2 for user+assistant pairs


# ── Public API ────────────────────────────────────────────────────────────────

def add_to_memory(user_msg: str, bot_msg: str, importance: int = 1) -> None:
    """
    Append a user/assistant pair with an optional importance score.

    Args:
        user_msg:   The user's raw message.
        bot_msg:    The bot's response.
        importance: Score 0–10 from UserProfile.update(); higher = more important.
    """
    _store.append(ScoredMessage(role="user",      content=user_msg, importance=importance))
    _store.append(ScoredMessage(role="assistant", content=bot_msg,  importance=importance))


def get_memory() -> List[ScoredMessage]:
    """Return the raw ScoredMessage list (used by token_guard smart trimmer)."""
    return list(_store)


def format_memory() -> List[Dict[str, Any]]:
    """
    Return structured message list compatible with OpenAI/Groq chat API.
    Drop-in replacement for the original format_memory().
    """
    return [m.to_dict() for m in _store]


def clear_memory() -> None:
    """Wipe all in-memory history."""
    _store.clear()


def rehydrate_memory(history_rows: list) -> None:
    """
    Populate *_store* from persisted SQLite rows after a server restart.

    Should be called once per session at initialisation time, **only when
    _store is empty**, so it is safe to call on every Streamlit rerun —
    subsequent calls are no-ops once the store is non-empty.

    Args:
        history_rows: List of dicts with keys ``user``, ``bot``, and
                      (optional) ``importance`` as returned by
                      ``database.get_chat_history()``.
    """
    if _store:
        # Already populated (e.g. user sent a message earlier in this run)
        return

    for row in history_rows:
        importance = int(row.get("importance", 1))
        _store.append(ScoredMessage(role="user",      content=row["user"], importance=importance))
        _store.append(ScoredMessage(role="assistant", content=row["bot"],  importance=importance))
