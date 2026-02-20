# Contributing to 🔥 Super RoastBot - Bug Hunt

Thank you for participating in the **Super RoastBot Bug Hunt Hackathon**! Your mission is to find the bugs, fix them, and bring the roast master back to life.

---

## 🚨 Contribution Rules (Strict Enforcement)

> **Read this section carefully before doing anything. Violations will result in your PR being closed without review.**

- ❌ **Do NOT open PRs for issues unless you are officially assigned**
- ❌ **Do NOT create new issues** - issues are created and managed only by organizers
- ❌ **PRs without a linked issue (or team number) will be closed immediately**
- ❌ **PRs for unassigned issues will be closed without merging**
- ❌ **Do NOT self-assign issues**
- ✅ **One issue per contributor at a time** - finish and submit before picking another
- ✅ **Only maintainers can assign, review, and merge PRs** - do not ask others to merge your PR
- ✅ **Every PR must include your Team Number** in the description
- ✅ **General improvement PRs** (bug fixes or enhancements outside existing issues) are allowed but reviewed strictly - you must still include your team number and clearly explain the change

---

## 📌 Issue Policy

- Issues are **created and managed only by organizers** - do not open your own issues
- To work on an issue, **comment on it requesting assignment** (e.g., *"I'd like to work on this, Team XX"*)
- **Wait for a maintainer to officially assign you** before writing any code
- Once assigned, you must submit your PR within **3-5 days** or the issue will be reassigned
- If you're stuck or unavailable, **comment on the issue** so maintainers can help or reassign

---

## 🚀 Reporting Bugs or Proposing Improvements

As part of this competition, **participants are not permitted to create new issues** in the repository.

If you identify:

- A functional bug  
- A UI/UX inconsistency  
- A documentation error  
- A minor or major enhancement  
- A refactor that improves code quality or maintainability  

You must **submit a Pull Request directly**.

---

### 📌 Important Guidelines

- ❌ Do **not** open a new issue for such findings.  
- ✅ Submit a Pull Request with a clear and structured description.  
- ✅ Include your **Team Number** in the PR description.  
- ✅ Clearly explain the problem and the rationale behind your proposed change.  
- ✅ Attach screenshots if the change affects UI.  

These submissions will be treated as **General Improvement Pull Requests** and will undergo **strict review** to ensure:

- Relevance to project scope  
- Code quality and maintainability  
- No unintended side effects  
- Compliance with project standards  

Maintainers reserve the right to close any PR that is:

- Trivial or low-effort  
- Outside the intended scope  
- Poorly documented  
- Not aligned with repository standards  

Please ensure that your contribution is meaningful, well-tested, and professionally presented.

---

## 🔐 Environment Variables & API Keys

This project requires access to LLM APIs (e.g., Google Gemini, OpenAI).

🚨 **Do NOT commit `.env` files or any API keys to the repository.**
🚨 **Do NOT hardcode credentials in your source code.**

If you need guidance on setting up your local environment keys, refer to the [README](https://github.com/gdg-charusat/PDF_QA_Bot%23readme) or contact the organizers.

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Bug Categories](#-bug-categories)
- [Development Workflow](#-development-workflow)
- [Pull Request Process](#-pull-request-process)

---

## 🛠 Tech Stack

This project uses:
- **UI Framework**: Streamlit
- **LLM API**: Groq (LLaMA 3.1)
- **RAG Engine**: FAISS + Sentence Transformers
- **Memory**: Custom Conversation Buffer
- **Environment**: Python 3.10+

---

## 🚀 Getting Started

### 1. Fork and Clone
1. **Fork** the repository to your own GitHub account.
2. **Clone** your fork locally:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/Super_RoastBot.git](https://github.com/YOUR-USERNAME/Super_RoastBot.git)
   cd Super_RoastBot
   ```

### 2. Setup Virtual Environment
```bash
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a .env file.

## 🐛 Bug Categories

- Config Errors: Bad URLs or variable names.
- Logic Errors: RAG or memory failures.
- Hyperparameters: Bad LLM output settings.
- Dependency Issues: Incorrect versions in requirements.txt.

## 🔄 Pull Request Process

- Team Number included in PR title.
- Bug Table completed in description.
- Clean Code: No debug print statements.

**Happy Hunting! 🔥**
