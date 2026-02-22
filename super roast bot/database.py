"""
SQLite Database Module for Persistent Chat Memory.
Stores chat history in a lightweight SQLite database for persistence across server restarts.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

# Database file path (same directory as this module)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.db")


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    return conn


def init_database():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT DEFAULT 'default'
        )
    """)
    
    conn.commit()
    conn.close()


def add_chat_entry(user_msg: str, bot_msg: str, session_id: str = "default") -> int:
    """
    Add a user-bot exchange to the database.
    
    Args:
        user_msg: The user's message
        bot_msg: The bot's response
        session_id: Optional session identifier for multi-user support
    
    Returns:
        The ID of the inserted row
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO chat_history (user_message, bot_response, session_id)
        VALUES (?, ?, ?)
    """, (user_msg, bot_msg, session_id))
    
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return row_id


def get_chat_history(session_id: str = "default", limit: Optional[int] = None) -> List[Dict]:
    """
    Retrieve chat history from the database.
    
    Args:
        session_id: Optional session identifier to filter by
        limit: Maximum number of entries to retrieve (most recent first)
    
    Returns:
        List of dictionaries containing chat entries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if limit:
        cursor.execute("""
            SELECT * FROM (
                SELECT id, user_message, bot_response, timestamp, session_id
                FROM chat_history
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            ) ORDER BY id ASC
        """, (session_id, limit))
    else:
        cursor.execute("""
            SELECT id, user_message, bot_response, timestamp, session_id
            FROM chat_history
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{"user": row["user_message"], "bot": row["bot_response"], 
             "timestamp": row["timestamp"], "id": row["id"]} for row in rows]


def clear_chat_history(session_id: str = "default"):
    """
    Clear all chat history for a specific session.
    
    Args:
        session_id: The session whose history should be cleared
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    
    conn.commit()
    conn.close()


def clear_all_history():
    """Clear all chat history from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM chat_history")
    
    conn.commit()
    conn.close()


def get_history_count(session_id: str = "default") -> int:
    """
    Get the number of chat entries for a session.
    
    Args:
        session_id: The session to count entries for
    
    Returns:
        Number of chat entries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) as count FROM chat_history WHERE session_id = ?", 
        (session_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result["count"]


# Initialize the database when the module is imported
init_database()
