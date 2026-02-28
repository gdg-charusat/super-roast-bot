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
