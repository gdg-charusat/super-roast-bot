"""
Context Token Guard — utils/token_guard.py

Smart token trimming that preserves HIGH-IMPORTANCE messages and discards
low-importance ones first.  Falls back gracefully to recency-based trimming
when importance scores are unavailable (e.g., plain dict messages).

Works with:
  - List[ScoredMessage]  — from the new memory.py  (importance-aware path)
  - List[Dict]           — legacy plain-dict format (recency fallback path)

PUBLIC API (unchanged from original):
  trim_chat_history(chat_history, tokenizer=None, max_tokens=3000)
  count_tokens(text, tokenizer=None)
"""

from __future__ import annotations

import warnings
from typing import Any


# ── Tokenizer bootstrap ───────────────────────────────────────────────────────

def _load_tokenizer():
    """Return tiktoken cl100k_base, or a word-count approximator as fallback."""
    try:
        import tiktoken  # type: ignore
        return tiktoken.get_encoding("cl100k_base")
    except ImportError:
        warnings.warn(
            "tiktoken not installed — token guard uses word-count approximation "
            "(1 word ≈ 1.3 tokens). Install with: pip install tiktoken",
            RuntimeWarning,
            stacklevel=3,
        )
        return _WordCountTokenizer()


class _WordCountTokenizer:
    """Fallback: splits on whitespace and scales by ~1.3 to approximate tokens."""
    def encode(self, text: str) -> list[int]:
        return [0] * int(len(text.split()) * 1.3 + 0.5)


_TOKENIZER = None


def _get_tokenizer():
    global _TOKENIZER
    if _TOKENIZER is None:
        _TOKENIZER = _load_tokenizer()
    return _TOKENIZER


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_content(msg: Any) -> str:
    """Extract text content from either a ScoredMessage or a plain dict."""
    if hasattr(msg, "content"):
        return msg.content or ""
    return msg.get("content", "") if isinstance(msg, dict) else ""


def _get_importance(msg: Any) -> int:
    """Return importance score; plain dicts score 1 (recency fallback)."""
    return getattr(msg, "importance", 1)


def _to_dict(msg: Any) -> dict:
    """Coerce any message type to a plain {role, content} dict."""
    if hasattr(msg, "to_dict"):
        return msg.to_dict()
    return dict(msg) if isinstance(msg, dict) else {"role": "user", "content": str(msg)}


def _count_tokens_list(messages: list, tokenizer) -> int:
    text = " ".join(_get_content(m) for m in messages if _get_content(m))
    return len(tokenizer.encode(text))


# ── Public API ────────────────────────────────────────────────────────────────

def trim_chat_history(
    chat_history: list[Any],
    tokenizer=None,
    max_tokens: int = 3000,
) -> list[dict[str, Any]]:
    """
    Prevent prompt overflow using importance-aware trimming.

    Strategy:
      1. If within budget → return as-is (converted to plain dicts).
      2. Identify the lowest-importance messages and drop them first.
      3. Always preserve the 2 most recent messages (last exchange) to
         maintain conversational continuity.
      4. If still over budget after dropping all low-importance messages,
         fall through to recency-based trimming.
      5. Preserve minimum message count even if over budget.

    Args:
        chat_history : list of ScoredMessage or plain dict messages.
        tokenizer    : optional tokenizer with .encode(str) → list.
        max_tokens   : token budget for the history block (default 3000).

    Returns:
        Trimmed list of plain {role, content} dicts, ready for the LLM API.
    """
    if tokenizer is None:
        tokenizer = _get_tokenizer()

    if not chat_history:
        return []

    # Work on a mutable copy; convert to list so we can index-delete
    working = list(chat_history)

    # ── Fast path: already within budget ──────────────────────────────────────
    current_tokens = _count_tokens_list(working, tokenizer)
    if current_tokens <= max_tokens:
        return [_to_dict(m) for m in working]

    # ── Importance-aware trimming ─────────────────────────────────────────────
    # Always preserve the last 2 messages (most recent user/assistant exchange).
    # Minimum 2 messages to maintain conversational continuity.
    PROTECTED_TAIL = 2
    MIN_MESSAGES = 2

    while _count_tokens_list(working, tokenizer) > max_tokens and len(working) > MIN_MESSAGES:
        # Identify candidates (all except protected tail)
        candidates = list(range(len(working) - PROTECTED_TAIL))
        if not candidates:
            break

        # Pick the message with the lowest importance score
        # Tie-break: prefer oldest (smallest index) to trim from the front
        drop_idx = min(candidates, key=lambda i: (_get_importance(working[i]), i))

        # Strategy: if this is a user message, also drop its assistant pair
        # (if found immediately after) to preserve coherence
        msg = working[drop_idx]
        if hasattr(msg, "role"):
            role = msg.role
        else:
            role = msg.get("role", "user")

        # Check if next message is the complementary role
        if (drop_idx + 1 < len(working) and
            drop_idx + 1 not in range(len(working) - PROTECTED_TAIL)):
            next_msg = working[drop_idx + 1]
            next_role = getattr(next_msg, "role", next_msg.get("role", "user"))
            complementary = (role == "user" and next_role == "assistant") or \
                           (role == "assistant" and next_role == "user")
            if complementary and len(working) > MIN_MESSAGES + 1:
                # Drop both for coherence
                if drop_idx + 1 >= drop_idx:
                    working.pop(drop_idx + 1)
                working.pop(drop_idx)
            else:
                working.pop(drop_idx)
        else:
            working.pop(drop_idx)

    # ── Hard recency fallback: still over budget? drop from front ─────────────
    while _count_tokens_list(working, tokenizer) > max_tokens and len(working) > MIN_MESSAGES:
        working.pop(0)

    # Ensure we always return at least the minimum (even if over budget)
    return [_to_dict(m) for m in working]


def count_tokens(text: str, tokenizer=None) -> int:
    """
    Convenience helper: count tokens in a plain string.

    Args:
        text      : The string to count tokens for.
        tokenizer : Optional tokenizer (defaults to module singleton).

    Returns:
        Integer token count.
    """
    if tokenizer is None:
        tokenizer = _get_tokenizer()
    return len(tokenizer.encode(text))
