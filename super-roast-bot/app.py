import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory

# ── Load environment variables from the .env file next to this script ──
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

if not GROQ_API_KEY:
    st.warning("⚠️ GROQ_API_KEY is not configured. Please add it to your `.env` file or the sidebar.")

# ── Configure Groq client (OpenAI-compatible) ──
if GROQ_API_KEY:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )
else:
    client = None

TEMPERATURE = 0.01       
MAX_TOKENS = 200      
MODEL_NAME = "llama-3.1-8b-instant"

def chat(user_input: str) -> str:
    if not user_input or user_input.isspace():
        return "You sent me nothing? Even your messages are empty, just like your GitHub contribution graph. 🔥"

    try:
        # Retrieve relevant roast context via RAG
        context = retrieve_context(user_input)

        # Get conversation history
        history = format_memory(st.session_state.session_id)

        # Build structured messages to avoid prompt injection and instruction mixing
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

        # Generate response from Groq using structured system prompt
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

        # Store in memory
        add_to_memory(user_input, reply, st.session_state.session_id)

        return reply

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "AuthenticationError" in error_msg or "expired_api_key" in error_msg:
            st.error("❌ Invalid or Expired API Key. Please check your Groq console and update the sidebar or `.env` file.")
        else:
            st.error(f"Error generating roast: {e}")
        return f"Even I broke trying to roast you. Error: {error_msg[:100]}"

st.set_page_config(page_title="Super RoastBot", page_icon="🔥", layout="centered")

st.title("🔥Super RoastBot")
st.caption("I roast harder than your code roasts your CPU")

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
    reply = response.choices[0].message.content
    add_to_memory(user_input, reply)
    return reply

st.title("🔥Super RoastBot")
if user_input := st.chat_input("Say something..."):
    with st.chat_message("assistant"):
        st.markdown(chat(user_input))