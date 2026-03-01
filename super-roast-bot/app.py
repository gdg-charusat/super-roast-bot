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
from groq import Groq
from dotenv import load_dotenv

from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory, get_memory
from utils.roast_mode import get_system_prompt, build_adaptive_prompt
from utils.token_guard import trim_chat_history
from utils.user_profile import UserProfile
from database import (
    add_chat_entry,
    save_user_profile,
    load_user_profile,
    clear_user_profile,
    clear_chat_history,
)

# ---------------- Environment ---------------- #
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_KEY"))

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


# ── Core chat functions ────────────────────────────────────────────────────────

def _validate_input(user_input):
    """
    Shared input validator.
    Returns (cleaned_input, error_message_or_None).
    Caller must return/yield the error string immediately when it is not None.
    """
    if not user_input or not isinstance(user_input, str):
        return None, "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"
    user_input = user_input.strip()
    if not user_input:
        return None, "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"
    if len(user_input) > 5000:
        return None, "Wow, you broke the character limit. That's impressive. 🔥 Please send a shorter message."
    return user_input, None


def _build_llm_messages(user_input: str, base_system_prompt: str):
    """
    Shared helper used by both chat() and chat_stream().
    Runs the full adaptive pipeline and returns (messages, importance, profile).
    """
    profile    = _get_profile()
    importance = profile.update(user_input)

    profile_snippet = profile.to_prompt_snippet()
    system_prompt   = build_adaptive_prompt(base_system_prompt, profile_snippet)

    context       = retrieve_context(user_input)
    raw_memory    = get_memory()
    trimmed_dicts = trim_chat_history(raw_memory, max_tokens=3000)

    messages = [
        {"role": "system", "content": system_prompt},
        *trimmed_dicts,
        {
            "role": "user",
            "content": f"Roast context:\n{context}\n\nCurrent message:\n{user_input}",
        },
    ]
    return messages, importance, profile


def chat_stream(user_input: str, base_system_prompt: str = SYSTEM_PROMPT):
    """
    Streaming variant — yields text chunks as they arrive from the LLM.

    Uses the identical adaptive-intelligence pipeline as chat():
      • UserProfile update & importance scoring
      • Adaptive system-prompt injection
      • RAG context retrieval
      • Importance-aware memory trimming
      • Persists the completed reply to memory + SQLite after streaming ends
    """
    user_input, err = _validate_input(user_input)
    if err:
        yield err
        return

    try:
        messages, importance, profile = _build_llm_messages(user_input, base_system_prompt)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True,
        )

        reply_parts = []
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                reply_parts.append(delta)
                yield delta

        # Persist the fully assembled reply after streaming completes
        reply = "".join(reply_parts)
        if reply:
            add_to_memory(user_input, reply, session_id=_get_session_id(), importance=importance)
            save_user_profile(_get_session_id(), profile.to_dict())

    except Exception as e:
        yield f"Even I broke trying to roast you. Error: {str(e)[:100]}"


def chat(user_input: str, base_system_prompt: str = SYSTEM_PROMPT) -> str:
    """Non-streaming variant with full adaptive intelligence."""

    user_input, err = _validate_input(user_input)
    if err:
        return err

    try:
        messages, importance, profile = _build_llm_messages(user_input, base_system_prompt)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        reply = response.choices[0].message.content

        add_to_memory(user_input, reply, session_id=_get_session_id(), importance=importance)
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

    enable_streaming = st.toggle(
        "⚡ Enable Streaming",
        value=True,
        help="Stream the roast token-by-token for a dramatic effect 🔥",
    )

    st.divider()

    if st.button("🗑️ Clear Chat"):
        sid = _get_session_id()
        st.session_state.messages = []
        clear_memory()
        clear_chat_history(sid)
        clear_user_profile(sid)
        if "user_profile" in st.session_state:
            del st.session_state["user_profile"]
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


# ── Chat state ─────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        try:
            if enable_streaming:
                reply = st.write_stream(chat_stream(user_input, base_system_prompt=system_prompt))
            else:
                with st.spinner("Cooking up a roast... 🍳"):
                    reply = chat(user_input, base_system_prompt=system_prompt)
                    st.markdown(reply)
        except Exception as e:
            reply = f"Even I broke trying to roast you. Error: {e}"
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})