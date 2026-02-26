from collections import deque

MAX_MEMORY = 10
chat_history = deque(maxlen=MAX_MEMORY)


def add_to_memory(user_msg: str, bot_msg: str):
    chat_history.append({"role": "user", "content": user_msg})
    chat_history.append({"role": "assistant", "content": bot_msg})


def get_memory() -> list:
    return list(chat_history)


def format_memory() -> list:
    """
    Returns structured message list directly.
    Compatible with OpenAI/Groq chat API.
    """
    return list(chat_history)


def clear_memory():
    chat_history.clear()