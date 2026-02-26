"""
FastAPI wrapper for RoastBot - For testing with Postman
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

from rag import retrieve_context
from prompt import SYSTEM_PROMPT
from memory import add_to_memory, format_memory, clear_memory

load_dotenv()

app = FastAPI(title="RoastBot API")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_KEY")
)

TEMPERATURE = 0.8
MAX_TOKENS = 512
MODEL_NAME = "llama-3.1-8b-instant"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """Generate a roast response"""
    if not request.message or request.message.isspace():
        return ChatResponse(reply="You sent me nothing? Even your messages are empty! 🔥")
    
    try:
        context = retrieve_context(request.message)
        history = format_memory()
        
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Use this roast context for inspiration: {context}\n\n"
            f"Recent conversation for context: {history}"
        )
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": request.message},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        
        reply = response.choices[0].message.content
        add_to_memory(request.message, reply)
        
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear")
def clear_endpoint():
    """Clear chat history"""
    clear_memory()
    return {"message": "Chat history cleared"}


@app.get("/")
def root():
    return {"message": "RoastBot API - Use POST /chat to get roasted!"}
