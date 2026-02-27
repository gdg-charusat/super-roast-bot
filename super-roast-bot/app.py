"""
Super RoastBot — app.py (Adaptive Roast Intelligence Edition)

New in this version:
  • UserProfile tracks skills, weaknesses, themes, and traits per session.
  • Every user message is scored for importance before being stored.
  • Scored memory survives token trimming based on importance, not just recency.
  • System prompt is dynamically augmented with the user's profile snippet.
  • Profile is persisted to SQLite so it survives page refreshes.
"""

import os
import uuid

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory, get_memory, rehydrate_memory
from utils.roast_mode import get_system_prompt, build_adaptive_prompt
from utils.token_guard import trim_chat_history
from utils.user_profile import UserProfile
from database import (
    add_chat_entry,
    get_chat_history,
    save_user_profile,
    load_user_profile,
    clear_user_profile,
    clear_chat_history,
)

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_KEY"),
)

TEMPERATURE = float(os.getenv("TEMPERATURE", 0.8))
MAX_TOKENS  = int(os.getenv("MAX_TOKENS", 512))
MODEL_NAME  = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")


# ── Session helpers ────────────────────────────────────────────────────────────

def _get_session_id() -> str:
    """Return a stable session ID for the current browser tab."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id


def _get_profile() -> UserProfile:
    """
    Return the UserProfile for this session, loading from SQLite on first call.
    """
    if "user_profile" not in st.session_state:
        sid   = _get_session_id()
        saved = load_user_profile(sid)
        if saved:
            st.session_state.user_profile = UserProfile.from_dict(saved)
        else:
            st.session_state.user_profile = UserProfile()
    return st.session_state.user_profile


def _init_session() -> None:
    """
    Initialise per-session state on the very first Streamlit run after a
    server restart.  Subsequent reruns are no-ops thanks to the
    ``_memory_rehydrated`` guard stored in ``st.session_state``.

    What this does:
    1. Loads the UserProfile from SQLite (via ``_get_profile()``).
    2. Fetches the last MAX_MEMORY turns of chat history from SQLite.
    3. Rehydrates the module-level ``_store`` deque in memory.py with
       importance-scored ScoredMessage objects so the LLM has context.
    4. Populates ``st.session_state.messages`` for the chat UI display.
    """
    if st.session_state.get("_memory_rehydrated"):
        return  # Already done this run

    _get_profile()  # Ensure profile is loaded

    sid  = _get_session_id()
    rows = get_chat_history(sid, limit=20)  # cap matches MAX_MEMORY in memory.py

    # 1. Rehydrate LLM memory store
    rehydrate_memory(rows)

    # 2. Rehydrate UI message list (only if it hasn't been set yet)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            entry
            for row in rows
            for entry in (
                {"role": "user",      "content": row["user"]},
                {"role": "assistant", "content": row["bot"]},
            )
        ]

    st.session_state["_memory_rehydrated"] = True


# ── Core chat function ─────────────────────────────────────────────────────────

def chat(user_input: str, base_system_prompt: str = SYSTEM_PROMPT) -> str:
    """Generate a personalised roast response with adaptive intelligence."""

    # ── Input validation ──────────────────────────────────────────────────────
    if not user_input or not isinstance(user_input, str):
        return "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"

    user_input = user_input.strip()
    if not user_input or len(user_input) == 0:
        return "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"

    if len(user_input) > 5000:
        user_input = user_input[:5000] + "..."
        return "Wow, you broke the character limit. That's impressive. 🔥 Please send a shorter message."

    try:
        # ── 1. Score the message and update user profile ───────────────────────
        profile    = _get_profile()
        importance = profile.update(user_input)

        # ── 2. Build adaptive system prompt ──────────────────────────────────
        profile_snippet = profile.to_prompt_snippet()
        system_prompt   = build_adaptive_prompt(base_system_prompt, profile_snippet)

        # ── 3. Retrieve RAG context ───────────────────────────────────────────
        context = retrieve_context(user_input)

        # ── 4. Get importance-scored memory and smart-trim it ─────────────────
        raw_memory    = get_memory()           # list[ScoredMessage]
        trimmed_dicts = trim_chat_history(raw_memory, max_tokens=3000)

        # ── 5. Assemble messages for the LLM ─────────────────────────────────
        messages = [
            {"role": "system", "content": system_prompt},
            *trimmed_dicts,
            {
                "role": "user",
                "content": (
                    f"Roast context:\n{context}\n\nCurrent message:\n{user_input}"
                ),
            },
        ]

        # ── 6. Call the LLM ───────────────────────────────────────────────────
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        reply = response.choices[0].message.content

        # ── 7. Persist to in-memory store and SQLite ──────────────────────────
        add_to_memory(user_input, reply, importance=importance)
        add_chat_entry(user_input, reply, session_id=_get_session_id(), importance=importance)

        # ── 8. Save updated profile to SQLite every turn ──────────────────────
        save_user_profile(_get_session_id(), profile.to_dict())

        return reply

    except Exception as e:
        st.error(f"Error generating roast: {e}")
        return f"Even I broke trying to roast you. Error: {str(e)[:100]}"


# ── Streamlit UI ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Super RoastBot 🔥", page_icon="🔥", layout="centered")

st.title("🔥 Super RoastBot")
st.caption("I roast harder than your code roasts your CPU")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")

    mode = st.selectbox(
        "🎚️ Roast Mode",
        ["Savage 🔥", "Funny 😏", "Friendly 🙂", "Professional 💼"],
        index=0,
    )

    system_prompt = get_system_prompt(mode)

    st.divider()

    if st.button("🗑️ Clear Chat"):
        sid = _get_session_id()
        st.session_state.messages = []
        clear_memory()
        clear_chat_history(sid)
        clear_user_profile(sid)
        if "user_profile" in st.session_state:
            del st.session_state["user_profile"]
        # Reset the rehydration guard so _init_session() stays clean
        st.session_state["_memory_rehydrated"] = False
        st.success("Chat cleared!")
        st.rerun()

    st.divider()

    # ── Adaptive profile panel (collapsible) ──────────────────────────────────
    profile = _get_profile()
    if profile.turn_count >= 2:
        with st.expander("🧠 What I know about you", expanded=False):
            if profile.skills:
                st.markdown("**Skills you've mentioned:**")
                for s in list(dict.fromkeys(profile.skills))[-3:]:
                    st.markdown(f"  • `{s}`")
            if profile.weaknesses:
                st.markdown("**Weaknesses I've caught:**")
                for w in list(dict.fromkeys(profile.weaknesses))[-3:]:
                    st.markdown(f"  • `{w}`")
            if profile.themes:
                top = [t for t, _ in profile.themes.most_common(3)]
                st.markdown(f"**Top topics:** {', '.join(top)}")
            if profile.traits:
                top_t = [t for t, _ in profile.traits.most_common(2)]
                st.markdown(f"**Personality:** {', '.join(top_t)}")
            st.markdown(f"**Turns:** `{profile.turn_count}`")

    st.divider()

    st.markdown(
        "**⚙️ Config (env-based):**\n"
        f"- Model: `{MODEL_NAME}`\n"
        f"- Temp: `{TEMPERATURE}`\n"
        f"- Max tokens: `{MAX_TOKENS}`"
    )


# ── Session initialisation (rehydrates memory + UI history from SQLite) ────────
_init_session()

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="😈" if msg["role"] == "assistant" else "🤡"):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Say something... if you dare 🔥"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🤡"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="😈"):
        with st.spinner("Cooking up a roast... 🍳"):
            reply = chat(user_input, base_system_prompt=system_prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})