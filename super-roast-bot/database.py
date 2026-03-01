"""
SQLite Database Module — database.py

Provides persistent storage for:
  - chat_history   : conversation turns per session
  - user_profiles  : adaptive roast intelligence profile per session

Backward-compatible: all original functions (add_chat_entry, get_chat_history,
clear_chat_history, get_session_count, get_total_messages) are unchanged.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")


# ── Connection + Schema ───────────────────────────────────────────────────────

def _get_connection():
    """Return a DB connection with both tables guaranteed to exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   TEXT    NOT NULL DEFAULT 'default',
            user_message TEXT    NOT NULL,
            bot_response TEXT    NOT NULL,
            importance   INTEGER NOT NULL DEFAULT 1,
            timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            session_id  TEXT PRIMARY KEY,
            profile_json TEXT NOT NULL,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    return conn


# ── Chat History (original API — untouched) ───────────────────────────────────

def add_chat_entry(user_msg: str, bot_msg: str, session_id: str = "default", importance: int = 1):
    """
    Add a new chat exchange to the database.

    Args:
        user_msg   : The user's message (will be truncated to 10000 chars for safety).
        bot_msg    : The bot's response (will be truncated to 10000 chars for safety).
        session_id : Session identifier for multi-user support.
        importance : Importance score (0-10) from the user profile engine.

    Note:
        Gracefully handles errors without crashing the chat.
    """
    # Validate and sanitize inputs
    if not isinstance(user_msg, str):
        user_msg = str(user_msg)
    if not isinstance(bot_msg, str):
        bot_msg = str(bot_msg)

    user_msg = user_msg[:10000].strip()  # Truncate for safety
    bot_msg = bot_msg[:10000].strip()
    importance = max(0, min(10, int(importance)))  # Clamp 0-10

    if not session_id or not isinstance(session_id, str):
        session_id = "default"

    try:
        with _get_connection() as conn:
            conn.execute(
                "INSERT INTO chat_history (session_id, user_message, bot_response, importance) VALUES (?, ?, ?, ?)",
                (session_id, user_msg, bot_msg, importance),
            )
    except sqlite3.Error as e:
        print(f"Error adding chat entry: {e}")
        # Gracefully continue; don't crash the chat


def get_chat_history(session_id: str = "default", limit: Optional[int] = None) -> List[Dict]:
    """
    Retrieve chat history for a session.

    Returns:
        List of {"user": ..., "bot": ..., "importance": ...} dicts in
        chronological order.  The "importance" key is included so callers
        can reconstruct ScoredMessage objects during memory rehydration.
    """
    with _get_connection() as conn:
        query = """
            SELECT user_message, bot_response, importance
            FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        rows = conn.execute(query, (session_id,)).fetchall()
        return [
            {
                "user": row["user_message"],
                "bot": row["bot_response"],
                "importance": row["importance"],
            }
            for row in reversed(rows)
        ]


def clear_chat_history(session_id: str = "default"):
    """Clear all chat history for a specific session."""
    with _get_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))


def get_session_count() -> int:
    """Total number of unique sessions."""
    with _get_connection() as conn:
        result = conn.execute("SELECT COUNT(DISTINCT session_id) FROM chat_history").fetchone()
        return result[0] if result else 0


def get_total_messages() -> int:
    """Total number of messages across all sessions."""
    with _get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()
        return result[0] if result else 0


# ── User Profile Persistence (new) ────────────────────────────────────────────

def save_user_profile(session_id: str, profile_dict: dict) -> None:
    """
    Upsert a user profile dict for the given session.

    Args:
        session_id   : Session identifier (required, will be validated).
        profile_dict : Output of UserProfile.to_dict().

    Raises:
        ValueError: If session_id is empty or profile_dict is not a dict.
    """
    if not session_id or not isinstance(session_id, str):
        raise ValueError(f"Invalid session_id: {session_id}")
    if not isinstance(profile_dict, dict):
        raise ValueError(f"profile_dict must be a dict, got {type(profile_dict)}")

    try:
        with _get_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_profiles (session_id, profile_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    profile_json = excluded.profile_json,
                    updated_at   = excluded.updated_at
                """,
                (session_id, json.dumps(profile_dict)),
            )
    except (sqlite3.Error, json.JSONDecodeError) as e:
        print(f"Error saving profile for {session_id}: {e}")
        # Gracefully continue; don't crash the chat


def load_user_profile(session_id: str) -> Optional[dict]:
    """
    Load an existing user profile dict, or None if none exists.

    Args:
        session_id : Session identifier.

    Returns:
        Profile dict (pass to UserProfile.from_dict()) or None if not found
        or on deserialization error.
    """
    if not session_id or not isinstance(session_id, str):
        return None

    try:
        with _get_connection() as conn:
            row = conn.execute(
                "SELECT profile_json FROM user_profiles WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row:
                return json.loads(row["profile_json"])
            return None
    except (sqlite3.Error, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading profile for {session_id}: {e}")
        return None


def clear_user_profile(session_id: str) -> None:
    """Delete the stored profile for a session."""
    with _get_connection() as conn:
        conn.execute("DELETE FROM user_profiles WHERE session_id = ?", (session_id,))


def init_database():
    """Initialize the database by ensuring the connection and tables exist.

    This is a lightweight helper for external modules that want to ensure the
    database schema is present before use. It simply opens and closes a
    connection which triggers table creation in `_get_connection`.
    """
    conn = _get_connection()
    conn.close()
