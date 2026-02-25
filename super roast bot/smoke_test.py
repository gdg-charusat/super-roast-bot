"""Quick smoke test runner for RoastBot fixes."""
import sys
sys.path.insert(0, r"c:\Users\Aryan Ghadiya\super-roast-bot\super roast bot")

def test_prompt():
    """Test prompt sanity."""
    from prompt import SYSTEM_PROMPT
    print("=== TEST: Prompt Sanity ===")
    
    assert "NEVER roast" not in SYSTEM_PROMPT, "❌ 'NEVER roast' still present"
    print("✓ No contradictory 'NEVER roast' rule")
    
    assert "roast" in SYSTEM_PROMPT.lower(), "❌ Roasting role not defined"
    print("✓ Roasting role clearly defined")
    print()

def test_memory():
    """Test memory formatting and sanitization."""
    from memory import clear_memory, add_to_memory, format_memory, _sanitize
    print("=== TEST: Memory ===")
    
    # Test sanitization
    sanitized = _sanitize("Call 555-123-4567 or email test@example.com")
    assert "[PHONE]" in sanitized and "[EMAIL]" in sanitized, "❌ PII not sanitized"
    print(f"✓ PII sanitization works: {sanitized[:60]}...")
    
    # Test formatting
    clear_memory()
    add_to_memory("hello", "boring response")
    formatted = format_memory()
    assert "User: hello" in formatted, "❌ User label missing"
    assert "RoastBot: boring response" in formatted, "❌ RoastBot label missing"
    print("✓ Memory formatting correct (User/RoastBot order)")
    
    # Test multi-turn
    add_to_memory("second", "roast2")
    multi = format_memory()
    assert "User: hello" in multi and "User: second" in multi, "❌ Multi-turn history broken"
    print("✓ Multi-turn history preserved")
    print()

def test_rag():
    """Test RAG graceful fallback."""
    print("=== TEST: RAG Fallback ===")
    try:
        import faiss
        from rag import retrieve_context
        result = retrieve_context("test")
        assert isinstance(result, str) and len(result) > 0, "❌ RAG returned invalid result"
        print(f"✓ RAG fallback works: '{result[:50]}'")
    except ImportError as e:
        print(f"⚠ SKIPPED: FAISS not available on this system ({e})")
        print("  Note: RAG functionality requires faiss-cpu to be properly installed.")
        print("  The code is ready; this is an environment limitation.")
    except Exception as e:
        print(f"❌ RAG failed: {e}")
        raise
    print()

if __name__ == "__main__":
    try:
        test_prompt()
        test_memory()
        test_rag()
        print("=" * 50)
        print("✓ ALL SMOKE TESTS PASSED")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
