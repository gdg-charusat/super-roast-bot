"""
RoastBot 🔥 — A RAG-based AI chatbot that roasts you into oblivion.
Built with Streamlit + Groq + FAISS.
"""

import os
from pathlib import Path
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory

# ── Load environment variables ──
load_dotenv()

# ── Configure Groq client (OpenAI-compatible) ──
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_KEY")
)

TEMPERATURE = 0.8       
MAX_TOKENS = 512        
MODEL_NAME = "llama-3.1-8b-instant"


def chat_stream(user_input: str):
    """Generate a streaming roast response for the user's input."""
    if not user_input or user_input.isspace():
        yield "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"
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
        yield f"Even I broke trying to roast you. Error: {str(e)[:100]}"


def chat(user_input: str) -> str:
    """Generate a roast response for the user's input."""

    if not user_input.strip():
        return "You sent me nothing? Even your messages are empty like your resume. 🔥"


    # Retrieve relevant roast context via RAG
    context = retrieve_context(user_input)
        # Get conversation history
        history = format_memory(st.session_state.session_id)

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

<<<<<<< HEAD:super roast bot/app.py
    # Store in memory
    add_to_memory(user_input, reply)
=======
        # Store in memory
        add_to_memory(user_input, reply, st.session_state.session_id)
>>>>>>> upstream/main:super-roast-bot/app.py

        return reply

st.set_page_config(page_title="Super RoastBot", page_icon="🔥", layout="centered")

st.title("🔥 Super RoastBot")
st.caption("I roast harder than your code roasts your CPU")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
<<<<<<< HEAD:super roast bot/app.py

=======
    
    enable_streaming = st.toggle("Enable Streaming", value=True, help="Show responses token-by-token")
    
>>>>>>> upstream/main:super-roast-bot/app.py
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        clear_memory(st.session_state.session_id)
        st.success("Chat cleared!")
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
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Display previous messages
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
                reply = st.write_stream(chat_stream(user_input))
            else:
                with st.spinner("Cooking up a roast... 🍳"):
                    reply = chat(user_input)
                    st.markdown(reply)
            
            # Store in memory
            add_to_memory(user_input, reply, st.session_state.session_id)
        except Exception as e:
            reply = f"Even I broke trying to roast you. Error: {e}"
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})