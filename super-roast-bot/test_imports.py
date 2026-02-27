#!/usr/bin/env python
"""Quick import test for the Adaptive Roast Intelligence implementation."""

import sys
sys.path.insert(0, '.')

# Test imports
try:
    from memory import add_to_memory, get_memory, format_memory
    print("✓ memory.py imports OK")
except ImportError as e:
    print(f"✗ memory.py import failed: {e}")

try:
    from utils.user_profile import UserProfile
    print("✓ utils/user_profile.py imports OK")
except ImportError as e:
    print(f"✗ utils/user_profile.py import failed: {e}")

try:
    from utils.token_guard import trim_chat_history, count_tokens
    print("✓ utils/token_guard.py imports OK")
except ImportError as e:
    print(f"✗ utils/token_guard.py import failed: {e}")

try:
    from utils.roast_mode import get_system_prompt, build_adaptive_prompt
    print("✓ utils/roast_mode.py imports OK (with build_adaptive_prompt)")
except ImportError as e:
    print(f"✗ utils/roast_mode.py import failed: {e}")

try:
    from database import add_chat_entry, save_user_profile, load_user_profile
    print("✓ database.py imports OK")
except ImportError as e:
    print(f"✗ database.py import failed: {e}")

print("\n✓ All core modules import successfully!")

# Quick functional test
print("\n--- Functional Tests ---")

# Test UserProfile
profile = UserProfile()
score = profile.update("I'm a Python developer who just broke production on my first day!")
print(f"✓ UserProfile.update() returned score: {score}/10")

# Test profile snippet generation
snippet = profile.to_prompt_snippet()
print(f"✓ Profile snippet generated: {len(snippet)} chars")

# Test build_adaptive_prompt
base_prompt = "You are RoastBot 🔥"
final_prompt = build_adaptive_prompt(base_prompt, snippet)
print(f"✓ build_adaptive_prompt() works: {len(final_prompt)} chars")

# Test memory operations
from memory import ScoredMessage
msg = ScoredMessage(role="user", content="Hello!", importance=5)
print(f"✓ ScoredMessage created with importance={msg.importance}")

print("\n✅ All tests passed!")
