"""
Context Token Guard — utils/token_guard.py
Prevents prompt overflow by trimming the oldest messages from chat history
before they are sent to the LLM.

Design constraints:
  - Does NOT touch memory.py, database.py, or any existing module.
  - Works with or without tiktoken installed (falls back to word-count).
  - Accepts the same chat_history list format used by app.py.
"""

from __future__ import annotations

import warnings
from typing import Any


# ── Tokenizer bootstrap ──────────────────────────────────────────────────────

def _load_tokenizer():
    """
    Return a tiktoken encoding if available, otherwise a dummy word-counter
    that satisfies the same .encode() interface.
    """
    try:
        import tiktoken  # type: ignore
        return tiktoken.get_encoding("cl100k_base")
    except ImportError:
        warnings.warn(
            "tiktoken is not installed. Token guard will use word-count "
            "approximation (1 word ≈ 1.3 tokens). "
            "Install tiktoken for exact token counting: pip install tiktoken",
            RuntimeWarning,
            stacklevel=3,
        )
        return _WordCountTokenizer()


class _WordCountTokenizer:
    """Fallback tokenizer: splits on whitespace and scales by ~1.3."""

    def encode(self, text: str) -> list[int]:
        words = text.split()
        # approximate: multiply word count by 1.3 to mimic sub-word tokens
        return [0] * int(len(words) * 1.3 + 0.5)


# Module-level singleton — loaded once on first import
_TOKENIZER = None


def _get_tokenizer():
    global _TOKENIZER
    if _TOKENIZER is None:
        _TOKENIZER = _load_tokenizer()
    return _TOKENIZER


# ── Public API ───────────────────────────────────────────────────────────────

def trim_chat_history(
    chat_history: list[dict[str, Any]],
    tokenizer=None,
    max_tokens: int = 3000,
) -> list[dict[str, Any]]:
    """
    Prevent prompt overflow by trimming the oldest messages from chat_history.

    The function mutates the list in-place AND returns it so callers can
    use either style::

        chat_history = trim_chat_history(chat_history)
        trim_chat_history(chat_history)          # also fine

    Args:
        chat_history:  List of message dicts with at minimum a "content" key.
        tokenizer:     Optional tokenizer with an .encode(str) method.
                       Defaults to tiktoken cl100k_base (or word-count fallback).
        max_tokens:    Maximum total token budget for the history block.

    Returns:
        The (possibly trimmed) chat_history list.
    """
    if tokenizer is None:
        tokenizer = _get_tokenizer()

    while True:
        # Build combined text from all messages that have a "content" field
        text = " ".join(
            m.get("content", "") for m in chat_history if m.get("content")
        )
        tokens = len(tokenizer.encode(text))

        if tokens <= max_tokens:
            break  # within budget — done

        if len(chat_history) > 2:
            chat_history.pop(0)  # drop oldest message
        else:
            # Fewer than 3 messages: can't trim further without losing context
            break

    return chat_history


def count_tokens(text: str, tokenizer=None) -> int:
    """
    Convenience helper: count tokens in a plain string.

    Args:
        text:      The string to count tokens in.
        tokenizer: Optional tokenizer (defaults to module singleton).

    Returns:
        Integer token count.
    """
    if tokenizer is None:
        tokenizer = _get_tokenizer()
    return len(tokenizer.encode(text))
