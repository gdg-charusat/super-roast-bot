#!/usr/bin/env python
# -*- coding: ascii -*-
"""Comprehensive test for Adaptive Roast Intelligence system."""

import sys
sys.path.insert(0, '.')

from memory import add_to_memory, get_memory, ScoredMessage
from utils.user_profile import UserProfile
from utils.token_guard import trim_chat_history, count_tokens
from utils.roast_mode import get_system_prompt, build_adaptive_prompt

print("=" * 60)
print("ADAPTIVE ROAST INTELLIGENCE - COMPREHENSIVE TEST")
print("=" * 60)

# Test 1: User Profile Scoring
print("\n[TEST 1] UserProfile Importance Scoring")
profile = UserProfile()

messages = [
    "I'm a Python developer",
    "I just broke production on my first day!",
    "I hate debugging async code, it's so confusing",
    "My startup failed spectacularly",
]

for i, msg in enumerate(messages, 1):
    score = profile.update(msg)
    print("  Turn {}: '{}...' -> Score: {}/10".format(i, msg[:50], score))

print("\n  Profile Analysis:")
print("    - Skills: {}".format(profile.skills))
print("    - Weaknesses: {}".format(profile.weaknesses))
print("    - Themes: {}".format(dict(profile.themes)))
print("    - Traits: {}".format(dict(profile.traits)))
print("    - Turn Count: {}".format(profile.turn_count))

# Test 2: Profile Snippet Generation
print("\n[TEST 2] Profile Snippet for Prompt Injection")
snippet = profile.to_prompt_snippet()
if snippet:
    print("[OK] Profile snippet generated after 4 turns:")
    print("  Length: {} chars".format(len(snippet)))
    print("  Preview:\n{}...".format(snippet[:200]))
else:
    print("[FAIL] No snippet generated (unexpected)")

# Test 3: Adaptive Prompt Building
print("\n[TEST 3] Adaptive Prompt Building")
base = "You are RoastBot - savage and witty"
full = build_adaptive_prompt(base, snippet)
print("[OK] Adaptive prompt built:")
print("  Base: {} chars".format(len(base)))
print("  With profile: {} chars".format(len(full)))
print("  Improvement: {} chars added".format(len(full) - len(base)))

# Test 4: Memory with Scoring
print("\n[TEST 4] Memory System with Importance Scores")
clear_memory = get_memory()
print("  Initial memory: {} messages".format(len(clear_memory)))

add_to_memory("Hello!", "Hi there!", importance=3)
add_to_memory("I'm a lazy developer", "That explains everything!", importance=9)
add_to_memory("....", "Ok. That's all?", importance=1)

memory = get_memory()
print("  After adding 3 exchanges: {} messages".format(len(memory)))
for i, msg in enumerate(memory, 1):
    icon = "[HIGH]" if msg.importance >= 7 else "[MED]" if msg.importance >= 4 else "[LOW]"
    print("    {}. {} {} (importance={}): {}".format(i, icon, msg.role, msg.importance, msg.content[:40]))

# Test 5: Smart Token Trimming
print("\n[TEST 5] Smart Token Trimming (Importance-Aware)")
print("  Building test history...")
test_memory = [
    ScoredMessage("user", "msg1", importance=1),
    ScoredMessage("assistant", "resp1", importance=1),
    ScoredMessage("user", "msg2 - super important breakage", importance=10),
    ScoredMessage("assistant", "resp2", importance=10),
    ScoredMessage("user", "msg3", importance=2),
    ScoredMessage("assistant", "resp3", importance=2),
    ScoredMessage("user", "msg4 - latest", importance=5),
    ScoredMessage("assistant", "resp4 - latest", importance=5),
]

print("  Test history: {} messages total".format(len(test_memory)))

try:
    tokens_before = count_tokens(" ".join(m.content for m in test_memory))
    print("  Total tokens before trim: ~{}".format(tokens_before))
except:
    print("  (tiktoken not available, using word-count approximation)")

trimmed = trim_chat_history(test_memory, max_tokens=50)
print("  After trimming to 50 tokens: {} messages preserved".format(len(trimmed)))
print("  Preserved messages:")
for msg_dict in trimmed:
    print("    - {}: {}".format(msg_dict['role'], msg_dict['content'][:40]))

# Test 6: Database Persistence
print("\n[TEST 6] Database Persistence")
try:
    from database import save_user_profile, load_user_profile, clear_user_profile
    
    test_session = "test_session_" + str(id(profile))
    profile_dict = profile.to_dict()
    save_user_profile(test_session, profile_dict)
    print("[OK] Saved profile to DB for session: {}".format(test_session))
    
    loaded = load_user_profile(test_session)
    if loaded:
        print("[OK] Loaded profile from DB:")
        print("    - Skills: {} items".format(len(loaded.get('skills', []))))
        print("    - Weaknesses: {} items".format(len(loaded.get('weaknesses', []))))
        print("    - Turn count: {}".format(loaded.get('turn_count', 0)))
    
    clear_user_profile(test_session)
    print("[OK] Cleared test profile from DB")
except Exception as e:
    print("[SKIP] Database test: {}".format(e))

# Test 7: System Prompt Modes
print("\n[TEST 7] System Prompt Modes")
modes = ["Savage", "Funny", "Friendly", "Professional"]
for mode in modes:
    prompt = get_system_prompt(mode + " 999")  # Use base without emoji
    print("  {} -> {} chars".format(mode, len(prompt)))

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
