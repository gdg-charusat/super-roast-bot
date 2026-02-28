"""
In-memory conversation store for RoastBot — feature/roast-intensity-token-guard.

Stores messages in OpenAI chat-API format ({"role": ..., "content": ...})
so the list returned by format_memory() can be passed directly to the LLM.

Memory is capped at MAX_TURNS full conversation turns (user + assistant pair).
The deque holds MAX_TURNS * 2 individual messages so each turn is never split.
"""

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


MAX_MEMORY = 10 
chat_history = deque(maxlen=MAX_MEMORY)

def add_to_memory(user_msg: str, bot_msg: str):
    chat_history.append({"user": user_msg, "bot": bot_msg})

def get_memory() -> list:
    """Return the raw list of message dicts (OpenAI format)."""
    return list(chat_history)

def format_memory() -> str:
    if not chat_history:
        return "No previous conversation."
    return "\n\n".join(
        [f"User: {entry['user']}\nAssistant: {entry['bot']}" for entry in chat_history]
    )

def clear_memory() -> None:
    """Wipe all stored messages."""
    chat_history.clear()
=======
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
