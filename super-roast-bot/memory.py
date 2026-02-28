"""
In-memory conversation store for RoastBot — feature/roast-intensity-token-guard.

Stores messages in OpenAI chat-API format ({"role": ..., "content": ...})
so the list returned by format_memory() can be passed directly to the LLM.

Memory is capped at MAX_TURNS full conversation turns (user + assistant pair).
The deque holds MAX_TURNS * 2 individual messages so each turn is never split.
"""

from collections import deque

<<<<<<< HEAD
MAX_MEMORY = 10 
chat_history = deque(maxlen=MAX_MEMORY)

def add_to_memory(user_msg: str, bot_msg: str):
    chat_history.append({"user": user_msg, "bot": bot_msg})
=======
MAX_TURNS: int = 10  # maximum conversation turns retained in memory

# Each slot holds one message dict: {"role": "user"|"assistant", "content": str}
# maxlen = MAX_TURNS * 2  so we always keep complete user/assistant pairs.
chat_history: deque = deque(maxlen=MAX_TURNS * 2)


def add_to_memory(user_msg: str, bot_msg: str) -> None:
    """Append a user/assistant exchange to the bounded memory."""
    chat_history.append({"role": "user",      "content": user_msg})
    chat_history.append({"role": "assistant", "content": bot_msg})

>>>>>>> fa21025 (fix: resolve all admin-reported issues on feature/roast-intensity-token-guard)

def get_memory() -> list:
    """Return the raw list of message dicts (OpenAI format)."""
    return list(chat_history)

<<<<<<< HEAD
def format_memory() -> str:
    if not chat_history:
        return "No previous conversation."
    return "\n\n".join(
        [f"User: {entry['user']}\nAssistant: {entry['bot']}" for entry in chat_history]
    )
=======

def format_memory() -> list:
    """
    Return the conversation history as a list of OpenAI-format message dicts.
    Pass the returned list directly into the messages array sent to the LLM.

    Returns an empty list when there is no history yet.
    """
    return list(chat_history)

>>>>>>> fa21025 (fix: resolve all admin-reported issues on feature/roast-intensity-token-guard)

def clear_memory() -> None:
    """Wipe all stored messages."""
    chat_history.clear()