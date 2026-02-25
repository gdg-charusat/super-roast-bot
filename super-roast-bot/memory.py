"""
Memory Module for RoastBot - Now with SQLite Persistent Storage!
Chat history persists across server restarts using SQLite database.
"""

from database import add_chat_entry, get_chat_history, clear_chat_history

MAX_MEMORY = 10


def add_to_memory(user_msg: str, bot_msg: str, session_id: str = "default"):
    """
    Add a user-bot exchange to persistent memory (SQLite database).
    
    Args:
        user_msg: The user's message
        bot_msg: The bot's response
        session_id: Optional session identifier for multi-user support
    """
    add_chat_entry(user_msg, bot_msg, session_id)


def get_memory(session_id: str = "default", limit: int = None) -> list:
    """
    Return current chat history as a list from the SQLite database.
    
    Args:
        session_id: Optional session identifier
        limit: Maximum number of entries to retrieve
    
    Returns:
        List of chat history entries
    """
    return get_chat_history(session_id, limit or MAX_MEMORY if MAX_MEMORY > 0 else None)


def clear_memory(session_id: str = "default"):
    """
    Clear all chat history for a session from the SQLite database.
    
    Args:
        session_id: The session whose history should be cleared
    """
    clear_chat_history(session_id)


def format_memory(session_id: str = "default") -> str:
    """
    Format chat history as a readable string for the LLM prompt.
    Retrieves from SQLite database for persistence.
    
    Args:
        session_id: Optional session identifier
    
    Returns:
        Formatted string of conversation history
    """
    # Get limited history for context (to avoid token overflow)
    chat_history = get_memory(session_id, MAX_MEMORY if MAX_MEMORY > 0 else None)
    
    if not chat_history:
        return "No previous conversation."
    
    # Fix the roles: it was showing User as RoastBot and vice versa
    return "\n\n".join(
        [f"User: {entry['user']}\nRoastBot: {entry['bot']}" for entry in chat_history]
    )