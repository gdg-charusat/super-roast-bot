"""
Adaptive Memory — memory.py

Stores chat history using SQLite for persistence.
Backward-compatible with importance-scored messages.
"""

from __future__ import annotations
from typing import Any, Dict, List
from database import add_chat_entry, get_chat_history, clear_chat_history

MAX_MEMORY = 20


def add_to_memory(user_msg: str, bot_msg: str, session_id: str = "default", importance: int = 1) -> None:
    """Add user/assistant pair to SQLite database."""
    add_chat_entry(user_msg, bot_msg, session_id, importance)


def get_memory(session_id: str = "default") -> List[Dict[str, Any]]:
    """Return chat history from SQLite as list of dicts."""
    history = get_chat_history(session_id, limit=MAX_MEMORY)
    result = []
    for entry in history:
        result.append({"role": "user", "content": entry["user"]})
        result.append({"role": "assistant", "content": entry["bot"]})
    return result


def format_memory(session_id: str = "default") -> List[Dict[str, Any]]:
    """Return structured message list compatible with OpenAI/Groq chat API."""
    return get_memory(session_id)


def clear_memory(session_id: str = "default") -> None:
    """Wipe all history for the session."""
    clear_chat_history(session_id)
