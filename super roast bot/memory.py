from collections import deque
from typing import List, Dict

# Maximum number of conversation exchanges to remember
MAX_MEMORY = 5

# Stores last N user-bot exchanges
chat_history: deque = deque(maxlen=MAX_MEMORY)


def add_to_memory(user_msg: str, bot_msg: str) -> None:
    """
    Add a user-bot exchange to memory.
    Automatically trims oldest entry if max size reached.
    """
    chat_history.append({
        "user": user_msg.strip(),
        "bot": bot_msg.strip()
    })


def get_memory() -> List[Dict[str, str]]:
    """
    Return current chat history as a list.
    """
    return list(chat_history)


def clear_memory() -> None:
    """
    Clear all stored conversation history.
    """
    chat_history.clear()


def format_memory() -> str:
    """
    Format chat history into a structured conversation
    suitable for LLM prompt injection.
    """
    if not chat_history:
        return "No previous conversation."

    return "\n\n".join(
        [
            f"User: {entry['user']}\nRoastBot: {entry['bot']}"
            for entry in chat_history
        ]
    )


def build_prompt(current_user_message: str) -> str:
    """
    Build the final prompt including memory and current user message.
    This ensures the LLM remembers previous context.
    """
    memory_block = format_memory()

    prompt = f"""
You are RoastBot, a sarcastic but funny AI assistant.

Previous Conversation:
{memory_block}

User: {current_user_message.strip()}
RoastBot:
"""
    return prompt.strip()
