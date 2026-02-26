"""
SQLite Database Module for RoastBot Chat History
Provides persistent storage for conversation history across sessions.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


# Database file path (relative to this module)
DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")


def _get_connection():
    """Get a database connection and ensure tables exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    
    # Create table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL DEFAULT 'default',
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def add_chat_entry(user_msg: str, bot_msg: str, session_id: str = "default"):
    """
    Add a new chat exchange to the database.
    
    Args:
        user_msg: The user's message
        bot_msg: The bot's response
        session_id: Session identifier for multi-user support
    """
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (session_id, user_message, bot_response) VALUES (?, ?, ?)",
            (session_id, user_msg, bot_msg)
        )


def get_chat_history(session_id: str = "default", limit: Optional[int] = None) -> List[Dict]:
    """
    Retrieve chat history for a session.
    
    Args:
        session_id: Session identifier
        limit: Maximum number of entries to retrieve (most recent first)
    
    Returns:
        List of chat entries as dictionaries with 'user' and 'bot' keys
    """
    with _get_connection() as conn:
        query = """
            SELECT user_message, bot_response 
            FROM chat_history 
            WHERE session_id = ? 
            ORDER BY timestamp DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        rows = conn.execute(query, (session_id,)).fetchall()
        
        # Return in chronological order (oldest first) and format for memory module
        return [
            {"user": row["user_message"], "bot": row["bot_response"]} 
            for row in reversed(rows)
        ]


def clear_chat_history(session_id: str = "default"):
    """
    Clear all chat history for a specific session.
    
    Args:
        session_id: Session identifier whose history should be cleared
    """
    with _get_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))


def get_session_count() -> int:
    """Get the total number of unique sessions."""
    with _get_connection() as conn:
        result = conn.execute("SELECT COUNT(DISTINCT session_id) FROM chat_history").fetchone()
        return result[0] if result else 0


def get_total_messages() -> int:
    """Get the total number of messages across all sessions."""
    with _get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()
        return result[0] if result else 0