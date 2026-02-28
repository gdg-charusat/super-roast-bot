from collections import deque

MAX_MEMORY = 10 
chat_history = deque(maxlen=MAX_MEMORY)

def add_to_memory(user_msg: str, bot_msg: str, session_id: str):
    chat_history.append({"user": user_msg, "bot": bot_msg})

def get_memory() -> list:
    return list(chat_history)

def format_memory(session_id: str) -> str:
    if not chat_history:
        return "No previous conversation."
    return "\n\n".join(
        [f"User: {entry['user']}\nAssistant: {entry['bot']}" for entry in chat_history]
    )

def clear_memory(session_id: str):
    chat_history.clear()