import os
import uuid
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory

# ---------------- Environment ---------------- #
load_dotenv()

# Initialize OpenAI/Groq client securely
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_KEY")
)

TEMPERATURE = 0.8
MAX_TOKENS = 512
MODEL_NAME = "llama-3.1-8b-instant"

# ---------------- Session State ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "enable_streaming" not in st.session_state:
    st.session_state.enable_streaming = True

# ---------------- Functions ---------------- #
def chat_stream(user_input: str):
    if not user_input or user_input.isspace():
        yield "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"
        return

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
            }
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True,
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"Even I broke trying to roast you. Error: {str(e)[:100]}"


def chat(user_input: str) -> str:
    if not user_input.strip():
        return "You sent me nothing? Even your messages are empty like your resume. 🔥"

    try:
        context = retrieve_context(user_input)
        history = format_memory(st.session_state.session_id)

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Use this roast context for inspiration:\n{context}\n\n"
            f"Recent conversation for context:\n{history}"
        )

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

        # Store in memory (only once)
        add_to_memory(user_input, reply, st.session_state.session_id)

        return reply

    except Exception as e:
        return f"Even I broke trying to roast you. Error: {str(e)[:100]}"


# ---------------- UI ---------------- #
st.set_page_config(page_title="Super RoastBot", page_icon="🔥", layout="centered")

st.title("🔥 Super RoastBot")
st.caption("I roast harder than your code roasts your CPU")

with st.sidebar:
    st.header("⚙️ Controls")
    st.session_state.enable_streaming = st.toggle(
        "Enable Streaming", value=st.session_state.enable_streaming
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        clear_memory(st.session_state.session_id)
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="😈" if msg["role"] == "assistant" else "🤡"):
        st.markdown(msg["content"])

# User input
if user_input := st.chat_input("Say something... if you dare 🔥"):

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="🤡"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="😈"):
        try:
            if st.session_state.enable_streaming:
                # Collect streaming chunks and accumulate
                reply_text = ""
                for chunk in chat_stream(user_input):
                    st.write(chunk, end="")  # stream to UI
                    reply_text += chunk

                add_to_memory(user_input, reply_text, st.session_state.session_id)
                reply = reply_text

            else:
                with st.spinner("Cooking up a roast... 🍳"):
                    reply = chat(user_input)
                    st.markdown(reply)

        except Exception as e:
            reply = f"Even I broke trying to roast you. Error: {e}"
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})