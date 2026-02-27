"""
Adaptive Roast Intelligence — utils/user_profile.py

Maintains a lightweight user profile derived from conversation history to
power personalised, non-repetitive roasts.

Profile tracks:
  - skills        : things the user claims to know / be good at
  - weaknesses    : slip-ups, self-confessed gaps, recurring mistakes
  - themes        : top topics that keep coming up (tech, relationships, etc.)
  - traits        : personality descriptors inferred from language
  - turn_count    : total exchanges — used to gate early-session generic roasts

Importance scoring for each memory entry:
  - self-disclosure keywords  → +3 (e.g., "I am", "I love", "my job")
  - emotional language        → +2 (e.g. "hate", "scared", "proud")
  - question asking           → +1 (signals confusion / weakness)
  - very short messages       → -1 (low information density)
  - repeated topic            → +1 bonus if topic already in themes
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

# ── Keyword banks ──────────────────────────────────────────────────────────────

_SKILL_PATTERNS = re.compile(
    r"\b(i (?:am|can|know|built|made|work|use|code|wrote|designed|developed|lead|created)|"
    r"my (?:project|work|job|startup|company|code|app|bot|api|skill)|"
    r"i(?:'m| am) (?:a|an) \w+)\b",
    re.IGNORECASE,
)

_WEAKNESS_PATTERNS = re.compile(
    r"\b(i (?:can'?t|couldn'?t|don'?t know|failed|forgot|broke|messed|struggle|suck|don'?t understand)|"
    r"my (?:code|bug|error|mistake|issue|problem)|"
    r"why (?:doesn'?t|isn'?t|won'?t|can'?t))\b",
    re.IGNORECASE,
)

_THEME_KEYWORDS: Dict[str, List[str]] = {
    "coding":        ["code", "python", "javascript", "bug", "git", "commit", "deploy", "debug", "function", "loop", "error", "exception", "stack", "api", "sql", "framework"],
    "career":        ["job", "interview", "resume", "cv", "salary", "promotion", "manager", "startup", "intern", "hire", "fired"],
    "relationships": ["girlfriend", "boyfriend", "date", "dating", "crush", "friend", "family", "mom", "dad", "ex"],
    "fitness":       ["gym", "workout", "diet", "weight", "run", "exercise", "fat", "muscle", "protein"],
    "gaming":        ["game", "gamer", "play", "level", "rank", "noob", "pvp", "fps", "rpg", "stream"],
    "ai_ml":         ["ai", "ml", "model", "neural", "gpt", "llm", "dataset", "train", "loss", "accuracy", "embedding"],
    "college":       ["college", "university", "degree", "exam", "assignment", "professor", "student", "gpa", "lecture"],
}

_EMOTION_WORDS = {
    "hate", "love", "scared", "proud", "angry", "excited", "sad", "happy",
    "frustrated", "confused", "lost", "embarrassed", "awesome", "terrible",
    "horrible", "amazing", "disgusting", "jealous",
}

_TRAIT_SIGNALS: Dict[str, List[str]] = {
    "overconfident": ["obviously", "trust me", "i know best", "clearly", "of course i", "no one can"],
    "self_deprecating": ["lol i", "haha i suck", "i know i'm bad", "don't roast me", "i'm the worst"],
    "curious":       ["how does", "why does", "can you explain", "what is", "what are", "how do i"],
    "defensive":     ["that's not fair", "actually i", "you're wrong", "not true", "stop roasting"],
}


# ── Dataclass ──────────────────────────────────────────────────────────────────

@dataclass
class UserProfile:
    """Live, in-memory profile for the current chat session."""

    skills: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    themes: Counter = field(default_factory=Counter)   # theme → mention count
    traits: Counter = field(default_factory=Counter)   # trait → signal count
    turn_count: int = 0

    # ── Ingestion ──────────────────────────────────────────────────────────────

    def update(self, user_msg: str, bot_reply: str = "") -> int:
        """
        Analyse a user message and bot reply, update the profile, and return an
        importance score (int, 0–10) for the memory entry.

        A higher score means the exchange should survive token trimming.

        Args:
            user_msg  : The user's message.
            bot_reply : The bot's response (used to validate engagement).

        Returns:
            Importance score (0-10 capped).
        """
        self.turn_count += 1
        score = 0
        msg_lower = user_msg.lower()

        # ── 1. Skills ──────────────────────────────────────────────────────────
        skill_hits = _SKILL_PATTERNS.findall(msg_lower)
        for hit in skill_hits:
            snippet = user_msg[:60].strip()
            if snippet not in self.skills:
                self.skills.append(snippet)
            score += 3

        # ── 2. Weaknesses ─────────────────────────────────────────────────────
        weak_hits = _WEAKNESS_PATTERNS.findall(msg_lower)
        for hit in weak_hits:
            snippet = user_msg[:60].strip()
            if snippet not in self.weaknesses:
                self.weaknesses.append(snippet)
            score += 3

        # ── 3. Themes ─────────────────────────────────────────────────────────
        words = set(re.findall(r"\b\w+\b", msg_lower))
        for theme, keywords in _THEME_KEYWORDS.items():
            matches = words & set(keywords)
            if matches:
                self.themes[theme] += len(matches)
                score += 1  # first hit
                if self.themes[theme] > 3:
                    score += 1  # recurring theme bonus

        # ── 4. Emotional language ─────────────────────────────────────────────
        emotion_hits = words & _EMOTION_WORDS
        if emotion_hits:
            score += 2

        # ── 5. Trait inference ────────────────────────────────────────────────
        for trait, signals in _TRAIT_SIGNALS.items():
            for signal in signals:
                if signal in msg_lower:
                    self.traits[trait] += 1
                    score += 1
                    break

        # ── 6. Question asking → weakness signal ─────────────────────────────
        if "?" in user_msg:
            score += 1

        # ── 7. Penalise trivial / very short messages ─────────────────────────
        if len(user_msg.split()) < 4:
            score = max(0, score - 1)

        # ── 8. Bonus: Bot engagement (if reply is substantive) ────────────────
        if bot_reply and len(bot_reply.split()) > 5:
            # Bot gave a thoughtful reply — this user message was valuable
            score = min(10, score + 1)

        return min(score, 10)  # cap at 10

    # ── Profile summary for prompt injection ──────────────────────────────────

    def to_prompt_snippet(self) -> str:
        """
        Return a compact text block to inject into the system prompt so the
        LLM can craft personalised roasts without being told explicitly.
        Returns an empty string during the first two turns (not enough signal).
        """
        if self.turn_count < 2:
            return ""

        parts: List[str] = []

        if self.skills:
            # Show last 3 unique skills
            unique_skills = list(dict.fromkeys(self.skills))[-3:]
            parts.append(f"Claims to be good at: {'; '.join(unique_skills)}")

        if self.weaknesses:
            unique_weak = list(dict.fromkeys(self.weaknesses))[-3:]
            parts.append(f"Has revealed weaknesses / slip-ups: {'; '.join(unique_weak)}")

        if self.themes:
            top_themes = [t for t, _ in self.themes.most_common(3)]
            parts.append(f"Recurring topics: {', '.join(top_themes)}")

        if self.traits:
            dominant_traits = [t for t, _ in self.traits.most_common(2)]
            parts.append(f"Personality signals: {', '.join(dominant_traits)}")

        if not parts:
            return ""

        return (
            "\n\n[USER PROFILE — use this to craft personalised roasts]\n"
            + "\n".join(f"• {p}" for p in parts)
            + "\n[/USER PROFILE]\n"
        )

    # ── Persistence helpers ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "skills": self.skills,
            "weaknesses": self.weaknesses,
            "themes": dict(self.themes),
            "traits": dict(self.traits),
            "turn_count": self.turn_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        p = cls()
        p.skills = data.get("skills", [])
        p.weaknesses = data.get("weaknesses", [])
        p.themes = Counter(data.get("themes", {}))
        p.traits = Counter(data.get("traits", {}))
        p.turn_count = data.get("turn_count", 0)
        return p

    def reset(self) -> None:
        """Reset the profile — called on chat clear."""
        self.skills.clear()
        self.weaknesses.clear()
        self.themes.clear()
        self.traits.clear()
        self.turn_count = 0
