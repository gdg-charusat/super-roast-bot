from collections import deque

MAX_MEMORY = 10
chat_history = deque(maxlen=MAX_MEMORY)


def add_to_memory(user_msg: str, bot_msg: str):
    """Add a user-bot exchange to memory. Automatically trims oldest entry."""
    chat_history.append({"user": user_msg, "bot": bot_msg})


def get_memory() -> list:
    """Return current chat history as a list."""
    return list(chat_history)


def clear_memory():
    """Clear all chat history."""
    chat_history.clear()


def format_memory() -> str:
    if not chat_history:
        return "No previous conversation."
    
    # Fix the roles: it was showing User as RoastBot and vice versa
    return "\n\n".join(
        [f"User: {entry['user']}\nAssistant: {entry['bot']}" for entry in chat_history]
    )
