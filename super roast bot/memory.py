from collections import deque
import re

MAX_MEMORY = 50

# Fallback global memory for non-Streamlit contexts (testing)
_fallback_history = deque(maxlen=MAX_MEMORY)

def _get_history():
    """Get chat history from Streamlit session state or fallback."""
    try:
        import streamlit as st
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = deque(maxlen=MAX_MEMORY)
        return st.session_state.chat_history
    except (ImportError, RuntimeError):
        # Streamlit not available or not in Streamlit context (e.g., testing)
        return _fallback_history


def _sanitize(text: str) -> str:
    """Basic sanitization: remove email-like strings and phone numbers."""
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    # Remove phone numbers (simple pattern)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    return text


def add_to_memory(user_msg: str, bot_msg: str):
    """Add a user-bot exchange to memory. Automatically trims oldest entry. Sanitizes PII."""
    chat_history = _get_history()
    sanitized_user = _sanitize(user_msg)
    sanitized_bot = _sanitize(bot_msg)
    chat_history.append({"user": sanitized_user, "bot": sanitized_bot})


def get_memory() -> list:
    """Return current chat history as a list."""
    return list(_get_history())


def clear_memory():
    """Clear all chat history."""
    _get_history().clear()


def format_memory() -> str:
    """Format chat history as a readable string for the LLM prompt."""
    chat_history = _get_history()
    if not chat_history:
        return "No previous conversation."

    # Using join for better performance than string concatenation in a loop
    return "\n\n".join(
        [f"User: {entry['user']}\nRoastBot: {entry['bot']}" for entry in chat_history]
    )
