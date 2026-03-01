# Adaptive Roast Intelligence - Testing Guide

## Overview
This guide will help you validate the Adaptive Roast Intelligence layer implementation for RoastBot. The system includes:

- **User Profile Tracking**: Learns user skills, weaknesses, themes, and personality traits
- **Importance-Based Memory**: Scores each message for importance (0-10)
- **Smart Token Trimming**: Preserves high-importance messages during context reduction
- **Dynamic Prompt Injection**: Augments system prompt with user profile for personalization
- **SQLite Persistence**: Saves profiles and chat history across sessions

---

## Pre-Test Setup

### 1. Install Dependencies
```bash
cd d:\TechSprint\super-roast-bot
pip install -r super-roast-bot/requirements.txt
```

**Key packages:**
- `openai` / `groq` API
- `streamlit` (UI framework)
- `faiss-cpu` (semantic search)
- `sentence-transformers` (embeddings)
- `tiktoken` (better token counting) - optional but recommended
- `PyPDF2` (PDF parsing for RAG)

### 2. Verify Environment
```bash
python -c "
from utils.roast_mode import build_adaptive_prompt
from utils.user_profile import UserProfile
from utils.token_guard import trim_chat_history
print('✓ All adaptive modules loaded successfully')
"
```

---

## Testing Levels

### Level 1: Unit Tests (Quick Validation)

#### 1a. Import Validation
```bash
cd super-roast-bot
python test_imports.py
```
**Expected output:** ✅ All core modules import successfully!

#### 1b. Comprehensive Functionality Tests
```bash
cd super-roast-bot
python test_comprehensive.py
```
**Expected output:**
- ✅ UserProfile importance scoring
- ✅ Profile snippet generation
- ✅ Adaptive prompt building
- ✅ Memory system with scoring
- ✅ Smart token trimming
- ✅ Database persistence
- ✅ System prompt modes

---

### Level 2: Integration Tests (End-to-End)

#### 2a. Test User Profile Learning
```python
from utils.user_profile import UserProfile

profile = UserProfile()

# Turn 1: Skill disclosure
score1 = profile.update("I'm a senior backend engineer at Google")
print(f"Score: {score1}")  # Should be high (6-7+) due to skill disclosure

# Turn 2: Weakness disclosure
score2 = profile.update("I struggle with CSS and frontend design")
print(f"Score: {score2}")  # Should be high due to weakness disclosure

# Turn 3: Emotional content
score3 = profile.update("I love debugging but hate meetings")
print(f"Score: {score3}")  # Should be moderate (2-3) due to emotion

# Check profile state
print(profile.to_dict())
```

**Verification:**
- Profile should capture skills: "I'm a senior backend engineer at Google"
- Profile should capture weaknesses: "I struggle with CSS and frontend design"
- Themes should include: "coding"
- Traits may include: emotional language detected

#### 2b. Test Memory Importance Scoring
```python
from memory import add_to_memory, get_memory
from utils.user_profile import UserProfile

profile = UserProfile()

# Simulate a conversation
messages = [
    ("I just deployed broken code to production", "That's a yikes from me 🔥"),
    ("What's a pointer?", "Uhh, that's CS 101..."),
    ("...", "ok"),
]

for user_msg, bot_msg in messages:
    importance = profile.update(user_msg, bot_msg)
    add_to_memory(user_msg, bot_msg, importance=importance)

# Check memory
for msg in get_memory():
    print(f"[{msg.importance}/10] {msg.role}: {msg.content[:40]}")
```

**Verification:**
- High-importance messages (significant disclosures) should have scores 6-10
- Low-importance messages (trivial) should have scores 1-3
- Memory should be sortable by importance

#### 2c. Test Token Trimming Preserves High-Value Context
```python
from memory import ScoredMessage
from utils.token_guard import trim_chat_history

# Create a large history with varied importance
history = [
    ScoredMessage("user", "throwaway comment", importance=1),
    ScoredMessage("assistant", "throwaway response", importance=1),
    ScoredMessage("user", "I built a successful startup", importance=10),
    ScoredMessage("assistant", "That's impressive", importance=10),
    ScoredMessage("user", "It failed though", importance=9),
    ScoredMessage("assistant", "Ouch", importance=9),
]

# Trim to very tight budget
trimmed = trim_chat_history(history, max_tokens=30)

print("After trimming:")
for msg in trimmed:
    print(f"  {msg['role']}: {msg['content']}")
```

**Verification:**
- Low-importance messages (importance=1) should be dropped first
- High-importance messages (importance=9-10) should be preserved
- Latest messages should always be preserved (cohesion)

#### 2d. Test Adaptive Prompt Injection
```python
from utils.roast_mode import get_system_prompt, build_adaptive_prompt
from utils.user_profile import UserProfile

profile = UserProfile()

# Build profile from conversation
profile.update("I'm a Python developer")
profile.update("I hate debugging")
profile.update("My code always breaks in production")
profile.update("But I love open source contributions")

# Get base prompt for a mode
base = get_system_prompt("Savage 🔥")
profile_snippet = profile.to_prompt_snippet()

# Build adaptive prompt
adaptive = build_adaptive_prompt(base, profile_snippet)

print(f"Base prompt length: {len(base)}")
print(f"Adaptive prompt length: {len(adaptive)}")
print(f"Profile injection added: {len(adaptive) - len(base)} chars")

# Verify profile info is in the prompt
if "Python" in adaptive and "debugging" in adaptive:
    print("✅ Profile information successfully injected into prompt")
```

**Verification:**
- Adaptive prompt should be longer than base prompt
- Adaptive prompt should contain user profile info (skills, weaknesses, themes)
- Profile info should follow format: "• Claims to be good at: ..."

---

### Level 3: Live Testing (Streamlit UI)

#### 3a. Start the Streamlit App
```bash
cd d:\TechSprint\super-roast-bot
streamlit run super-roast-bot/app.py
```

#### 3b. Test Profile Learning
1. **First message**: Type something with a skill disclosure
   - Example: "I'm a DevOps engineer with 5 years experience"
   - Expected: Bot roasts you, profile captures the skill
   - Check sidebar: "What I know about you" should show the skill

2. **Second message**: Type something with a weakness
   - Example: "I can't write good SQL queries"
   - Expected: Bot roasts you about the weakness
   - Check sidebar: Weakness should appear under "Weaknesses I've caught"

3. **Continue 3-4+ more messages**: Establish patterns
   - Expected: Profile learns themes (coding appears in multiple turns)
   - Sidebar should show "Top topics: coding, ..."

#### 3c. Test Roast Personalization
After 5+ messages building profile:
1. Send a message related to your established theme
2. Compare with roasts from the first turn
3. **Expected**: Later roasts should be more personalized, referencing your established skills/weaknesses

#### 3d. Test Clear & Reset
1. Click "Clear Chat" in sidebar
2. **Expected**:
   - Chat history disappears
   - "What I know about you" panel disappears
   - DB is cleaned up
3. Send a new message
4. **Expected**: Profile should reset (sidebar shows empty until 2+ new turns)

#### 3e. Test Memory Persistence
1. Have a conversation (5+ messages)
2. Refresh the browser or restart streamlit (Ctrl+C and rerun)
3. **Expected**: Previous messages appear in chat and sidebar shows the learned profile

#### 3f. Test Mode Switching
1. In sidebar, change "Roast Mode" to different intensities:
   - "Savage 🔥" → Most aggressive
   - "Funny 😏" → Light-hearted
   - "Friendly 🙂" → Gentle teasing
   - "Professional 💼" → Office-appropriate
2. Send new messages in each mode
3. **Expected**: Roasts should match the intensity level

---

## Advanced Testing

### Performance Testing
```python
import time
from utils.user_profile import UserProfile
from memory import add_to_memory, get_memory
from utils.token_guard import trim_chat_history

# Simulate 100-turn conversation
profile = UserProfile()
start = time.time()

for i in range(100):
    msg = f"Message {i} with varying content patterns and keywords"
    score = profile.update(msg)
    add_to_memory(msg, f"Response {i}", importance=score)

elapsed = time.time() - start
print(f"100 turns processed in {elapsed:.2f}s")

# Trim under load
trimmed = trim_chat_history(get_memory(), max_tokens=2000)
print(f"Trimmed to {len(trimmed)} messages: {elapsed:.2f}s total")
```

**Expected**: Should complete in <1 second for 100 turns

### Database Integrity
```python
from database import save_user_profile, load_user_profile, clear_user_profile
from utils.user_profile import UserProfile

# Test round-trip
original = UserProfile()
original.update("Test message 1")

profile_dict = original.to_dict()
save_user_profile("test_integrity", profile_dict)

loaded_dict = load_user_profile("test_integrity")
restored = UserProfile.from_dict(loaded_dict)

# Verify
assert original.skills == restored.skills
assert original.turn_count == restored.turn_count
print("✅ Database round-trip integrity verified")

clear_user_profile("test_integrity")
```

---

## Troubleshooting

### Issue: "tiktoken not installed" warning
**Solution**: This is a warning, not a critical error. The system falls back to word-count approximation.
```bash
pip install tiktoken
```

### Issue: Database locked errors
**Solution**: Ensure only one instance of the app is running. Close all Streamlit windows and restart.
```bash
# Kill any lingering processes
taskkill /F /IM python.exe  # (or lsof -i :8501 on Mac/Linux)
```

### Issue: Profile not persisting
**Solution**: Check that `chat_history.db` exists in `super-roast-bot/`
```bash
ls -la super-roast-bot/chat_history.db
```

### Issue: Adaptive prompt too long
**Solution**: This is normal. Prompts can grow as profiles build. If exceeding token limits, first trim memory more aggressively, then trim profile snippet.

---

## Success Criteria Checklist

- [ ] All unit tests pass (`test_imports.py`, `test_comprehensive.py`)
- [ ] User profile learns skills from "I am..." statements
- [ ] User profile learns weaknesses from "I can't..." statements
- [ ] High-importance messages survive token trimming
- [ ] Profile snippet injects into system prompt
- [ ] Roasts become more personalized after 5+ turns
- [ ] Clear Chat properly resets profile and memory
- [ ] Database persists profile across browser refreshes
- [ ] Different roast modes produce different tones
- [ ] No crashes on empty input or very long input
- [ ] Performance is responsive (<2s per turn)

---

## PR Checklist

Before raising your PR, verify:

- [ ] All tests pass
- [ ] No debug print statements left
- [ ] No extra `.db` files (only `chat_history.db` should exist)
- [ ] No extra `.md` files created (keep the repo clean)
- [ ] Code follows existing style
- [ ] Docstrings updated
- [ ] No breaking changes to existing APIs
- [ ] Database schema changes are backward-compatible

---

## Performance Targets

- **Profile Update**: <10ms per message
- **Memory Trimming**: <50ms for 100-message history
- **Token Counting**: <100ms with tiktoken
- **Database Save**: <50ms
- **Full Chat Response**: <3 seconds (dominated by LLM, not adaptive logic)

---

## Questions?

Refer to:
- [Memory Implementation](memory.py) for storage details
- [User Profile](utils/user_profile.py) for scoring logic
- [Token Guard](utils/token_guard.py) for trimming strategy
- [Roast Mode](utils/roast_mode.py) for prompt injection
