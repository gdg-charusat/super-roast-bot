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
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from rag import retrieve_context
from memory import add_to_memory, format_memory, clear_memory
from utils.roast_mode import get_system_prompt
from utils.token_guard import trim_chat_history

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

TEMPERATURE = float(os.getenv("TEMPERATURE", 0.8))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 512))
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")


def chat(user_input: str, system_prompt: str = "") -> str:
    """Generate a roast response while preserving history structure."""

    if not user_input or user_input.isspace():
        return "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"

    try:
        # Retrieve RAG context
        context = retrieve_context(user_input)

        # Get raw structured memory (list of OpenAI-format dicts)
        history = format_memory()

        # Ensure history is a list
        if not isinstance(history, list):
            history = []

        # Trim using token guard
        raw_history = trim_chat_history(history, max_tokens=3000)

        # Build proper structured messages
        messages = [
            {"role": "system", "content": system_prompt},
            *raw_history,
            {
                "role": "user",
                "content": f"Roast context:\n{context}\n\nCurrent message:\n{user_input}",
            },
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        reply = response.choices[0].message.content

        # Save to memory
        add_to_memory(user_input, reply)

        return reply

    except Exception as e:
        st.error(f"Error generating roast: {e}")
        return f"Even I broke trying to roast you. Error: {str(e)[:100]}"


# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="Super RoastBot", page_icon="🔥", layout="centered")

st.title("🔥 Super RoastBot")
st.caption("I roast harder than your code roasts your CPU")

# Sidebar
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
        st.success("Chat cleared!")
        st.rerun()

    st.divider()

    st.markdown(
        "**⚙️ Config (env-based):**\n"
        f"- Model: `{MODEL_NAME}`\n"
        f"- Temp: `{TEMPERATURE}`\n"
        f"- Max tokens: `{MAX_TOKENS}`"
    )


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="😈" if msg["role"] == "assistant" else "🤡"):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Say something... if you dare 🔥"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🤡"):
        st.markdown(user_input)

    # Generate roast
    with st.chat_message("assistant", avatar="😈"):
        with st.spinner("Cooking up a roast... 🍳"):
            reply = chat(user_input, system_prompt=system_prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})