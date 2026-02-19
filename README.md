# 🔥 RoastBot — Bug Hunt Hackathon Challenge

> **Your mission:** This RoastBot is completely broken. Find all the bugs, fix them, and bring the roast master back to life!

## 🤔 What is RoastBot?

RoastBot is a **RAG-powered AI chatbot** that roasts you based on what you say. It uses:

- **Streamlit** — for the web UI
- **Groq API** (LLaMA 3.1) — for generating savage roasts
- **FAISS + Sentence Transformers** — for retrieving relevant roast context
- **Conversation Memory** — so it remembers what you said and roasts you even harder

**But right now... it's broken.** The code is riddled with bugs — some will crash the app, some will make it produce garbage, and some are sneaky enough that you won't notice until you look closely.

---

## 📁 Project Structure

```
├── app.py              # Main Streamlit app + Groq API client
├── rag.py              # RAG module (chunking, embedding, FAISS retrieval)
├── prompt.py           # System prompt for the LLM
├── memory.py           # Conversation memory management
├── .env                # Environment variables (API keys)
├── requirements.txt    # Python dependencies
└── data/
    └── roast_data.txt  # Roast knowledge base
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
> ⚠️ **Hint:** If installation fails, that might be your first bug...

### 4. Set up your API key
- Get a free API key from [Groq Console](https://console.groq.com/)
- Check the `.env` file and make sure your key is configured correctly

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🎯 Challenge Rules

1. **Find and fix all the bugs** hidden across the codebase
2. Bugs exist in **every file** — Python code, config files, even the requirements
3. Some bugs **crash** the app, some make it produce **bad/gibberish output**, and some are **subtle logic errors**
4. **Do NOT modify `data/roast_data.txt`** — the data file is clean
5. When you fix a bug, **document it** — write what was wrong and what you changed

---

## 🐛 Types of Bugs to Look For

| Category | Examples |
|----------|---------|
| 🔧 **Config Errors** | Wrong URLs, bad API keys, mismatched variable names |
| 📐 **Bad Hyperparameters** | Values that are technically valid but produce terrible results |
| ✏️ **Typos** | Misspelled names that cause lookup failures |
| 🧠 **Logic Errors** | Code that runs but does the wrong thing |
| 📦 **Dependency Issues** | Missing or misspelled packages |
| 💬 **Prompt Engineering** | Instructions that sabotage the AI's behavior |

---

## ✅ How to Know You're Done

When RoastBot is fully fixed, it should:

- ✅ Start without any errors
- ✅ Accept user input and respond with **creative, funny roasts**
- ✅ Use relevant context from the roast knowledge base (RAG working)
- ✅ Remember previous messages in the conversation (memory working)
- ✅ Generate responses that are **multiple sentences long**, not cut off

---

## 📝 Submission Format

For each bug you find, document:

```
Bug #: [number]
File: [filename]
Line: [line number]
What was wrong: [description]
Fix: [what you changed]
```

---

## 💡 Tips

- Read the **error messages carefully** — they often point you straight to the bug
- If the app runs but output is bad, check the **hyperparameters** and **prompt**
- Compare related files — does the `.env` variable name match what the code expects?
- **Don't overthink it** — some bugs are literally just typos

---

**Good luck, and may your roasts be savage! 🔥**
