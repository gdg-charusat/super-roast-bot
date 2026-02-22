"""
RoastBot 🔥 — A RAG-based AI chatbot that roasts you into oblivion.
Built with Streamlit + Groq + FAISS.
"""

import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory

# ── Load environment variables ──
load_dotenv()

# ── Configure Groq client (OpenAI-compatible) ──
client = OpenAI(
    base_url="https://api.groq.com/v1",
    api_key=os.getenv("GROQ_KEY")
)

TEMPERATURE = 0.8       
MAX_TOKENS = 512        
MODEL_NAME = "llama-3.1-8b-instant"


def chat(user_input: str) -> str:
    """Generate a roast response for the user's input."""

    # used .strip to remove whitespaces 
    if not user_input or user_input.isspace():
        return "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"


    # Retrieve relevant roast context via RAG
    context = retrieve_context(user_input)

    # Get conversation history
    history = format_memory()

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Use this roast context for inspiration: {context}\n\n"
        f"Recent conversation for context: {history}"
    )
    # Generate response from Groq
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    reply = response.choices[0].message.content

    # Store in memory
    add_to_memory(user_input, reply)

    return reply

st.set_page_config(page_title="Super RoastBot", page_icon="🔥", layout="centered")

st.title("🔥Super RoastBot")
st.caption("I roast harder than your code roasts your CPU")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        clear_memory()
        st.rerun()
    st.divider()
    st.markdown(
        "**How it works:**\n"
        "1. Your message is sent to RAG retrieval\n"
        "2. Relevant roast knowledge is fetched\n"
        "3. Groq crafts a personalized roast\n"
        "4. You cry. Repeat."
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        with st.spinner("Cooking up a roast... 🍳"):
            try:
                reply = chat(user_input)
                st.markdown(reply)
            except Exception as e:
                reply = f"Even I broke trying to roast you. Error: {e}"
                st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
