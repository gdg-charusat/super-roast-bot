from collections import deque

MAX_MEMORY = 10 # Fixed from 0 to 10
chat_history = deque(maxlen=MAX_MEMORY)

def add_to_memory(user_msg: str, bot_msg: str):
    chat_history.append({"user": user_msg, "bot": bot_msg})

def format_memory() -> str:
    if not chat_history:
        return "No previous conversation."
    
    # Fixed role labels (User vs Assistant)
    return "\n\n".join(
        [f"User: {entry['user']}\nAssistant: {entry['bot']}" for entry in chat_history]
    )

def clear_memory():
    chat_history.clear()