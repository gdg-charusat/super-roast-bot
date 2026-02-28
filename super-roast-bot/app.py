"""
RoastBot 🔥 — A RAG-based AI chatbot that roasts you into oblivion.
Built with Streamlit + Groq + FAISS.
"""

import os
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

# ── Validate the API key is present and not a placeholder ──
def get_validated_api_key():
    # Priority 1: Sidebar override
    if "api_key_override" in st.session_state and st.session_state.api_key_override:
        return st.session_state.api_key_override.strip()
    
    # Priority 2: Environment variable
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        # Strip quotes and whitespace that often cause 401s
        env_key = env_key.strip().replace('"', '').replace("'", "")
        if env_key and env_key not in ("YOUR API KEY", "your_groq_api_key_here"):
            return env_key
    return None

GROQ_API_KEY = get_validated_api_key()

# ── Configure Groq client (OpenAI-compatible) ──
if GROQ_API_KEY:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )
else:
    client = None

TEMPERATURE = float(os.getenv("TEMPERATURE", 0.8))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 512))
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")


def chat_stream(user_input: str):
    """Generate a streaming roast response for the user's input."""
    if not user_input or user_input.isspace():
        yield "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"
        return

    if not client:
        yield "⚠️ I can't roast you without an API key. Stop being poor and add one to the sidebar or `.env`. 🔥"
        return

    try:
        context = retrieve_context(user_input)
        history = format_memory(st.session_state.session_id)
        
        messages = [{
            "role": "user",
            "content": (
                f"Roast context (from knowledge base):\n{context}\n\n"
                f"Recent conversation:\n{history}\n\n"
                f"Current message: {user_input}"
            ),
        }]
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "AuthenticationError" in error_msg or "expired_api_key" in error_msg:
            yield "❌ Invalid or Expired API Key. Please update the sidebar or your `.env` file."
        else:
            yield f"Even I broke trying to roast you. Error: {error_msg[:100]}"


def chat(user_input: str) -> str:
    """Generate a roast response for the user's input using structured messages."""
    if not user_input or user_input.isspace():
        return "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"

    if not client:
        return "⚠️ I can't roast you without an API key. Stop being poor and add one to the sidebar or `.env`. 🔥"

    try:
        context = retrieve_context(user_input)
        history = format_memory(st.session_state.session_id)
        
        messages = [
            {
                "role": "user",
                "content": (
                    f"Roast context (from knowledge base):\n{context}\n\n"
                    f"Recent conversation:\n{history}\n\n"
                    f"Current message: {user_input}"
                ),
            },
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages,
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        reply = response.choices[0].message.content
        return reply

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "AuthenticationError" in error_msg or "expired_api_key" in error_msg:
            st.error("❌ Invalid or Expired API Key. Please update the sidebar or your `.env` file.")
        else:
            st.error(f"Error generating roast: {e}")
        return f"Even I broke trying to roast you. Error: {error_msg[:100]}"


st.set_page_config(page_title="Super RoastBot", page_icon="🔥", layout="centered")
st.title("🔥Super RoastBot")
st.caption("I roast harder than your code roasts your CPU")

if not GROQ_API_KEY:
    st.warning("⚠️ GROQ_API_KEY is not configured. Please add it to your `.env` file or use the sidebar.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    
    enable_streaming = st.toggle("Enable Streaming", value=True, help="Show responses token-by-token")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        clear_memory(st.session_state.session_id)
        st.success("Chat cleared!")
        st.rerun()

    st.divider()
    st.markdown("**🔑 API Key Management**")
    new_key = st.text_input("Override GROQ_API_KEY", type="password", placeholder="gsk_...")
    if st.button("Apply Key"):
        st.session_state.api_key_override = new_key
        st.rerun()
    if "api_key_override" in st.session_state and st.session_state.api_key_override:
        if st.button("Reset to .env Key"):
            del st.session_state.api_key_override
            st.rerun()
    st.divider()
    st.markdown(
        "**How it works:**\n"
        "1. Your message is sent to RAG retrieval\n"
        "2. Relevant roast knowledge is fetched\n"
        "3. Groq crafts a personalized roast\n"
        "4. You cry. Repeat."
    )
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
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Display chat history
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
        try:
            if enable_streaming:
                reply = st.write_stream(chat_stream(user_input))
            else:
                with st.spinner("Cooking up a roast... 🍳"):
                    reply = chat(user_input)
                    st.markdown(reply)
            # Store in memory
            add_to_memory(user_input, reply, st.session_state.session_id)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            reply = f"Even I broke trying to roast you. Error: {e}"
            st.error(reply)
