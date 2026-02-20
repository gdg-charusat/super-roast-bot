# Contributing to Super RoastBot — Bug Hunt Hackathon Challenge

Thank you for your interest in contributing to Super RoastBot as part of the
GDG CHARUSAT Open Source Contri Sprintathon! 🎉

---

## 🚨 Contribution Rules (Strict Enforcement)

Read this section carefully before doing anything. Violations will result
in your PR being closed without review.

❌ Do NOT open PRs for issues unless you are officially assigned  
❌ PRs without a linked issue (or team number) will be closed immediately  
❌ PRs for unassigned issues will be closed without merging  
❌ Do NOT self-assign issues  
✅ Contributors may create new issues for bugs, enhancements, or documentation improvements, following the Issue Guidelines below  
✅ One issue per contributor at a time - finish and submit before picking another  
✅ Only maintainers can assign, review, and merge PRs - do not ask others to merge your PR  
✅ Every PR must include your Team Number in the description  
✅ General improvement PRs (bug fixes or enhancements outside existing issues) are allowed but reviewed strictly - you must still include your team number and clearly explain the change  

---

## 📌 Issue Policy

Contributors may create new issues for:

- Bugs found across any file in the codebase
- UI/UX inconsistencies in the Streamlit interface
- Documentation improvements
- Feature suggestions

Before creating a new issue, check that a similar issue does not already exist.  
Use clear, descriptive titles and provide proper details.  
To work on an issue, comment on it requesting assignment (e.g., "I'd like to work on this, Team XX").  
Wait for a maintainer to officially assign you before writing any code.  
Once assigned, you must submit your PR within 3-5 days or the issue will be reassigned.  
If you're stuck or unavailable, comment on the issue so maintainers can help or reassign.  

---

## 🚀 Reporting Bugs or Proposing Improvements

If you identify:

- A crash bug in `app.py`, `rag.py`, `memory.py`, or `prompt.py`
- A logic error that causes bad or gibberish roast output
- A misconfigured hyperparameter producing terrible results
- A dependency issue in `requirements.txt`
- A prompt engineering problem sabotaging the AI's behaviour
- A documentation error in any `.md` file

You must create a new issue and wait for it to be approved.

---

## 📌 Important Guidelines

✅ Open a new issue describing the problem clearly and wait for maintainer acknowledgment before submitting a Pull Request.  
✅ Submit a Pull Request with a clear and structured description.  
✅ Include your Team Number in the PR description.  
✅ Clearly explain the bug and what you changed to fix it.  
✅ Attach screenshots if the change affects the Streamlit UI.  
✅ Document every bug fix using the submission format described below.  

Maintainers reserve the right to close any PR that is:

- Trivial or low-effort
- Outside the intended scope
- Poorly documented
- Not aligned with repository standards

Please ensure that your contribution is meaningful, well-tested, and professionally presented.

---

## 🔐 Environment Variables & Secrets

This project requires a Groq API key to run.

🚨 Do NOT share your API key in issues or pull requests.  
🚨 Do NOT commit your `.env` file to the repository.  
🚨 Never hardcode API keys directly in any Python file.  

If you need environment variable details to work on an assigned issue, please contact the organizers privately:

📱 WhatsApp: +91-8320699419 || +91-8347036131 || +91-9227448882  
📧 Email: charmidodiya2005@gmail.com || jadejakrishnapal04@gmail.com || aaleya2604@gmail.com  

Environment details will be shared only after the issue is officially assigned to you.

---

## 🛠 Tech Stack

This project uses:

- **Language:** Python 3.9+
- **UI Framework:** Streamlit
- **LLM:** Groq API (LLaMA 3.1)
- **RAG:** FAISS + Sentence Transformers
- **Memory:** Conversation memory management via `memory.py`
- **Prompt:** System prompt engineering via `prompt.py`
- **Environment:** `.env` file for API key configuration

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9 or higher
- pip (comes with Python)
- Git

---

## 🚀 Getting Started

### Step 1: Fork the Repository

Navigate to [https://github.com/gdg-charusat/super-roast-bot](https://github.com/gdg-charusat/super-roast-bot)  
Click the **Fork** button in the top-right corner.  
This creates a copy of the repository in your GitHub account.

### Step 2: Clone Your Fork

Clone the forked repository to your local machine:
```bash
git clone https://github.com/YOUR-USERNAME/super-roast-bot.git
cd super-roast-bot
```

Replace `YOUR-USERNAME` with your GitHub username.

### Step 3: Add Upstream Remote

Add the original repository as an upstream remote to keep your fork synced:
```bash
git remote add upstream https://github.com/gdg-charusat/super-roast-bot.git
```

Verify the remotes:
```bash
git remote -v
```

You should see:

- `origin` - your fork ([https://github.com/YOUR-USERNAME/super-roast-bot.git](https://github.com/YOUR-USERNAME/super-roast-bot.git))
- `upstream` - the original repository ([https://github.com/gdg-charusat/super-roast-bot.git](https://github.com/gdg-charusat/super-roast-bot.git))

### Step 4: Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **Hint:** If installation fails, that might be your first bug...

### Step 6: Set Up Your API Key

Get a free API key 
Check the `.env` file and make sure your key is configured correctly.  
The `.env` file should look like this:
```
GROQ_API_KEY=your_api_key_here
```

### Step 7: Run the App to Verify Setup
```bash
streamlit run app.py
```

Navigate to [http://localhost:8501](http://localhost:8501) in your browser.  
If the app loads and accepts input, your setup is working.

### Step 8: Create a New Branch

> **IMPORTANT:** Always create a new branch for your work. Never work directly on the `main` branch.
```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout -b fix/your-bug-description
```

**Branch Naming Convention:**

- `fix/` — for bug fixes (e.g., `fix/requirements-typo`)
- `docs/` — for documentation (e.g., `docs/update-readme`)
- `refactor/` — for code improvements (e.g., `refactor/rag-chunking`)
- `style/` — for UI changes (e.g., `style/streamlit-layout`)

---

## 💻 Development Workflow

### 1. Pick an Issue

Browse the Issues page at [https://github.com/gdg-charusat/super-roast-bot/issues](https://github.com/gdg-charusat/super-roast-bot/issues)

Look for issues labelled:
- `good first issue` or `level: beginner` — for beginners
- `level: intermediate` — for intermediate contributors
- `level: advanced` — for advanced contributors

Comment on the issue with your request and team number, e.g.:
> "Hi, I'd like to work on this issue. - Team 07"

Wait to be officially assigned — do not start writing any code until a maintainer assigns you.  
Do not work on an issue already assigned to someone else.

### 2. Understand the Project Structure

Before writing any code, understand what each file does:

- `app.py` — Main Streamlit app and Groq API client
- `rag.py` — RAG module handling chunking, embedding, and FAISS retrieval
- `prompt.py` — System prompt for the LLM
- `memory.py` — Conversation memory management
- `.env` — Environment variables (API keys)
- `requirements.txt` — Python dependencies
- `data/roast_data.txt` — Roast knowledge base (**do NOT modify this file**)

### 3. Find and Fix Bugs

This is a bug hunt challenge. Bugs exist across every file. Here are the categories to look for:

| Category | Examples |
|----------|---------|
| 🔧 Config Errors | Wrong URLs, bad API keys, mismatched variable names |
| 📐 Bad Hyperparameters | Values that are technically valid but produce terrible results |
| ✏️ Typos | Misspelled names that cause lookup failures |
| 🧠 Logic Errors | Code that runs but does the wrong thing |
| 📦 Dependency Issues | Missing or misspelled packages in `requirements.txt` |
| 💬 Prompt Engineering | Instructions in `prompt.py` that sabotage the AI's behaviour |

### 4. Document Every Bug You Fix

For every single bug you find and fix, add it to your PR description using this exact format:
```
Bug #: [number]
File: [filename]
Line: [line number]
What was wrong: [description]
Fix: [what you changed]
```

PRs without documented bug fixes will not be reviewed.

### 5. How to Know You Are Done

When RoastBot is fully fixed, it should:

- ✅ Start without any errors
- ✅ Accept user input and respond with creative, funny roasts
- ✅ Use relevant context from the roast knowledge base (RAG working)
- ✅ Remember previous messages in the conversation (memory working)
- ✅ Generate responses that are multiple sentences long and not cut off

### 6. Test Your Fixes

Run the app and verify it works end to end:
```bash
streamlit run app.py
```

Then test these scenarios manually:

- Type a message and confirm you get a roast response
- Send multiple messages and confirm the bot remembers earlier ones
- Confirm responses are complete and not cut off mid-sentence
- Confirm the app starts with zero error messages in the terminal

### 7. Commit Your Changes

Write clear, descriptive commit messages:
```bash
git add .
git commit -m "fix: correct misspelled package name in requirements.txt"
```

**Commit Message Format:**

- `fix:` — bug fix (e.g., `fix: correct FAISS retrieval parameter`)
- `docs:` — documentation changes (e.g., `docs: update setup instructions`)
- `refactor:` — code improvement (e.g., `refactor: simplify memory logic`)
- `style:` — UI or formatting changes (e.g., `style: improve chat layout`)
- `chore:` — maintenance tasks (e.g., `chore: update requirements.txt`)

### 8. Push to Your Fork
```bash
git push origin fix/your-bug-description
```

### 9. Create a Pull Request

Go to your fork on GitHub: `https://github.com/YOUR-USERNAME/super-roast-bot`  
Click **"Compare & pull request"** button.  
Fill out the PR completely:

- **Title:** Clear, descriptive title (e.g., `Fix 4 bugs across rag.py and requirements.txt`)
- **Team Number:** You must state your team number (e.g., Team 07) — PRs without this will be closed
- **Issue Reference:** Link the assigned issue (e.g., `Closes #5`)
- **Bug Documentation:** List every bug you fixed using the format above
- **Screenshots:** Add before/after screenshots showing the broken vs fixed app

Click **"Create pull request"**

---

## 📌 Issue Guidelines

### Finding Issues

Issues are categorised by difficulty level.

**🟢 Beginner Level (Good First Issues)**

- Typos in variable names or function calls
- Missing or misspelled package in `requirements.txt`
- Wrong environment variable name in `.env` or `app.py`
- Minor documentation fixes

Labels: `good first issue`, `level: beginner`

**🟡 Intermediate Level**

- Logic errors in `memory.py` or `rag.py`
- Bad hyperparameter values causing poor output quality
- Prompt engineering issues in `prompt.py` sabotaging roast quality
- FAISS retrieval configuration problems

Labels: `level: intermediate`

**🔴 Advanced Level**

- Complex RAG pipeline bugs affecting retrieval accuracy
- Groq API integration issues causing silent failures
- Multi-file bugs where one error causes cascading failures across modules

Labels: `level: advanced`

---

### How to Request an Issue

Find an unassigned issue you want to work on.  
Comment on the issue with this format:

> "I'd like to work on this. - Team [your team number]"

Wait for a maintainer to assign it to you — this is mandatory.  
Once assigned, start working and submit your PR within 3–5 days.  
If you can't complete it in time, comment to let maintainers know.

⚠️ Before opening a new issue, ensure:

- The issue does not already exist
- It is clearly documented with file name and line number if possible
- It aligns with the project scope (bug fixes, RAG pipeline, Streamlit UI, prompt engineering)

---

### Creating a New Issue

When creating a new issue:

- Use a clear and descriptive title (e.g., `Bug: FAISS index dimension mismatch in rag.py`)
- Add a detailed description covering:
  - Which file and line number the bug is in
  - What the bug causes (crash, bad output, silent failure)
  - Steps to reproduce
  - Expected vs actual behaviour
  - Screenshots of any error messages if applicable
- Wait for maintainer review before starting work

---

## 🔄 Pull Request Process

### PR Requirements — Non-Negotiable

PRs that don't meet **ALL** of the following will be closed without review:

- [ ] Team number stated in the PR description (e.g., Team XX)
- [ ] Linked to your assigned issue via `Closes #issue-number`
- [ ] You are the assigned contributor for that issue
- [ ] PR is raised after assignment, not before
- [ ] Every bug fix is documented using the required format

### Before Submitting

- [ ] `streamlit run app.py` starts with zero errors in the terminal
- [ ] App accepts user input and returns a roast response
- [ ] Conversation memory works across multiple messages
- [ ] Responses are complete and not cut off
- [ ] No API keys or `.env` file committed
- [ ] Commit messages follow the conventional format above
- [ ] Before/after screenshots included in PR description

### PR Review Process

A maintainer will review your PR within 24–48 hours.  
You may be asked to make changes — respond promptly.  
Make requested changes and push to the same branch (PR auto-updates).  
Only maintainers can approve and merge — do not request peers to merge.

### Addressing Review Comments

Make the requested changes, then:
```bash
git add .
git commit -m "fix: address review comments on memory bug"
git push origin fix/your-bug-description
```

---

## 🆘 Need Help?

- **Issue Discussion:** Comment on the issue you are working on
- **WhatsApp:** +91-8320699419 || +91-8347036131 || +91-9227448882
- **Email:** charmidodiya2005@gmail.com || jadejakrishnapal04@gmail.com || aaleya2604@gmail.com

---

## 🎯 Tips for Success

**Read Error Messages Carefully:** They often point you straight to the bug. Don't skip past them.

**Check Variable Names:** The most common bugs are mismatched variable names between `.env` and `app.py`. Compare them character by character.

**Run the App First:** Before fixing anything, run `streamlit run app.py` and note every error you see. Make a list before touching any code.

**Check Requirements First:** `requirements.txt` bugs will stop you from even installing the project. Fix those before anything else.

**Compare Related Files:** Does the variable name in `.env` exactly match what `app.py` reads? Does the function name in `rag.py` exactly match what `app.py` calls?

**Don't Overthink It:** Some bugs are literally just typos. If something looks slightly off, it probably is.

**Document As You Go:** Write down each bug as you find it rather than trying to remember everything at the end.

**Be Patient:** Code review takes time — be responsive to feedback when it comes.

**Have Fun:** This is a roast bot. It is supposed to be savage. Enjoy debugging it! 🔥

---

## 📜 Code of Conduct

Please be respectful and professional in all interactions. We are here to learn and help each other grow. Discrimination, harassment, or disrespectful behaviour of any kind will not be tolerated.

Happy Bug Hunting! 🐛🔥

If you have any questions or need clarification, feel free to reach out to the maintainers or ask in the issue comments.

Thank you for contributing to Super RoastBot!
