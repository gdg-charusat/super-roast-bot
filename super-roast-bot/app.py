import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_KEY")
)

TEMPERATURE = 0.01       
MAX_TOKENS = 200      
MODEL_NAME = "llama-3.1-8b-instant"

def chat(user_input: str) -> str:
    if not user_input or user_input.isspace():
        return "You sent me nothing? 🔥"
    context = retrieve_context(user_input)
    history = format_memory()
    prompt = f"{SYSTEM_PROMPT}\n\nContext: {context}\n\nHistory: {history}"
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_input}],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    reply = response.choices[0].message.content
    add_to_memory(user_input, reply)
    return reply

st.title("🔥Super RoastBot")
if user_input := st.chat_input("Say something..."):
    with st.chat_message("assistant"):
        st.markdown(chat(user_input))