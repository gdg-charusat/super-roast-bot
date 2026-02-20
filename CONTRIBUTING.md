# Contributing to Super RoastBot

Thank you for your interest in contributing to **Super RoastBot** as part of the **Bug Hunt Hackathon Challenge**! 🔥

Your mission is simple: fix the broken RoastBot and bring the roast master back to life.

------------------------------------------------------------------------

## 🚨 Contribution Rules (Strict Enforcement)

> **Read this section carefully before starting. Violations may result > in your PR being closed without review.**

-   ❌ Do NOT open PRs unless you are officially assigned an issue
-   ❌ Do NOT create new issues --- issues are created and managed only by organizers
-   ❌ PRs without a linked issue (or team number) will be closed immediately
-   ❌ PRs for unassigned issues will be closed without merging
-   ❌ Do NOT self-assign issues
-   ✅ One issue per contributor at a time
-   ✅ Only maintainers can assign, review, and merge PRs
-   ✅ Every PR must include your Team Number in the description
-   ✅ Every bug fix must be properly documented

------------------------------------------------------------------------

## 📌 Issue Policy

-   Issues are created and managed only by organizers
-   Comment requesting assignment: "I'd like to work on this. --- Team XX"
-   Wait for official assignment before writing code
-   Submit PR within 3--5 days after assignment
-   If stuck, comment on the issue

------------------------------------------------------------------------

## 🚀 Reporting Bugs or Proposing Improvements

Participants are not permitted to create new issues.

If you identify: 
- A crash bug
- A configuration issue
- A dependency error
- A logic mistake
- A prompt engineering flaw
- A performance or retrieval issue

Submit a Pull Request directly.

### Important Guidelines

-   Do not open a new issue
-   Submit a structured PR
-   Include Team Number
-   Clearly explain what was broken and how you fixed it

------------------------------------------------------------------------

## 🔐 Environment Variables & Secrets

This project uses a Groq API key.

Do NOT commit `.env` files. Do NOT hardcode API keys. Do NOT expose secrets in PRs.

Example `.env`:

GROQ_API_KEY=your_api_key_here

------------------------------------------------------------------------

## 🛠 Tech Stack

-   Streamlit
-   Groq API (LLaMA 3.1)
-   Sentence Transformers
-   FAISS
-   Python

------------------------------------------------------------------------

## ✅ Prerequisites

-   Python 3.9+
-   pip
-   Git
-   Virtual environment support
-   Groq API key

------------------------------------------------------------------------

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/SuperRoastBot.git 
cd SuperRoastBot
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows: ```bash venv\Scripts\activate ```

macOS/Linux: ```bash source venv/bin/activate ```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create `.env` file:

GROQ_API_KEY=your_api_key_here

### Run the App

```bash
streamlit run app.py
```

------------------------------------------------------------------------

## 💻 Development Workflow

### Branch Naming

-   fix/
-   refactor/
-   chore/
-   docs/

Example:

git checkout -b fix/issue-description

------------------------------------------------------------------------

## 🐛 Bug Categories

-   Config Errors
-   Bad Hyperparameters
-   Typos
-   Logic Errors
-   Dependency Issues
-   Prompt Engineering Issues

------------------------------------------------------------------------

## 🔄 Pull Request Requirements

-   Team number included
-   Linked assigned issue
-   Proper bug documentation
-   No `.env` committed
-   App runs successfully

------------------------------------------------------------------------

## 📜 Code of Conduct

Be respectful and professional in all interactions.

------------------------------------------------------------------------

🔥 Fix it. Test it. Break it again. Fix it properly.

Good luck!
