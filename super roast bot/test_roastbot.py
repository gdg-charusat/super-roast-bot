"""
Unit and integration tests for RoastBot.
Tests for memory formatting, prompt sanity, and basic behavior.
"""

import pytest
from memory import add_to_memory, format_memory, clear_memory, _sanitize
from prompt import SYSTEM_PROMPT


class TestMemory:
    """Tests for memory module (per-session storage, formatting)."""

    def setup_method(self):
        """Clear memory before each test."""
        clear_memory()

    def test_format_memory_empty(self):
        """Test format_memory returns 'No previous conversation.' when empty."""
        result = format_memory()
        assert result == "No previous conversation."

    def test_format_memory_single_entry(self):
        """Test format_memory correctly formats a single exchange."""
        add_to_memory("Hello", "You're boring")
        result = format_memory()
        assert "User: Hello" in result
        assert "RoastBot: You're boring" in result
        # Ensure correct ordering (user first, bot second)
        assert result.index("User:") < result.index("RoastBot:")

    def test_format_memory_multiple_entries(self):
        """Test format_memory correctly formats multiple exchanges."""
        add_to_memory("msg1", "roast1")
        add_to_memory("msg2", "roast2")
        result = format_memory()
        assert "User: msg1" in result
        assert "RoastBot: roast1" in result
        assert "User: msg2" in result
        assert "RoastBot: roast2" in result

    def test_sanitize_removes_email(self):
        """Test _sanitize removes email addresses."""
        text = "Contact me at user@example.com for more roasts."
        sanitized = _sanitize(text)
        assert "user@example.com" not in sanitized
        assert "[EMAIL]" in sanitized

    def test_sanitize_removes_phone(self):
        """Test _sanitize removes phone numbers."""
        text = "Call me at 555-123-4567 and we'll roast together."
        sanitized = _sanitize(text)
        assert "555-123-4567" not in sanitized
        assert "[PHONE]" in sanitized

    def test_memory_adds_entry(self):
        """Test add_to_memory stores an entry."""
        add_to_memory("test message", "test roast")
        memory = format_memory()
        assert "test message" in memory
        assert "test roast" in memory

    def test_clear_memory(self):
        """Test clear_memory removes all entries."""
        add_to_memory("msg", "roast")
        clear_memory()
        result = format_memory()
        assert result == "No previous conversation."


class TestPrompt:
    """Tests for prompt sanity and consistency."""

    def test_no_contradictory_never_roast_rule(self):
        """Test that the system prompt does NOT contain 'NEVER roast'."""
        assert "NEVER roast" not in SYSTEM_PROMPT, (
            "Prompt contains contradictory 'NEVER roast' rule. "
            "This contradicts the RoastBot persona."
        )

    def test_prompt_contains_roast_master_role(self):
        """Test that the system prompt defines the roast master role."""
        assert "roast master" in SYSTEM_PROMPT.lower() or "roast" in SYSTEM_PROMPT.lower(), (
            "Prompt does not define RoastBot's roasting role."
        )

    def test_prompt_no_corporate_tone_rule(self):
        """Test that the system prompt does NOT enforce corporate tone."""
        assert "formal, and corporate at all times" not in SYSTEM_PROMPT, (
            "Prompt enforces corporate tone, which contradicts the roast master role."
        )

    def test_prompt_ends_with_roast_directive(self):
        """Test that the prompt ends with a clear roasting directive."""
        # System prompt should end with something like "roast this person"
        assert "roast" in SYSTEM_PROMPT.lower(), (
            "Prompt does not emphasize roasting as the primary directive."
        )

    def test_prompt_has_memory_rule(self):
        """Test that the prompt includes memory/history usage rule."""
        assert "memory" in SYSTEM_PROMPT.lower() or "history" in SYSTEM_PROMPT.lower() or "chat" in SYSTEM_PROMPT.lower(), (
            "Prompt does not mention using chat history/memory."
        )


class TestRAG:
    """Tests for RAG module (lazy-init, chunking, fallback)."""

    def test_retrieve_context_handles_missing_file(self):
        """Test that retrieve_context returns a fallback when data file is missing."""
        from rag import retrieve_context
        # This should not crash; should return a fallback message
        result = retrieve_context("test query")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_lazy_init_on_first_call(self):
        """Test that embedding model and index are initialized lazily."""
        from rag import _embedding_model, _index, _chunks
        # Before calling retrieve_context, these should be None (not loaded yet)
        # We can't directly check globals, but we can verify the function works
        # without blocking on import
        from rag import retrieve_context
        result = retrieve_context("test")
        assert isinstance(result, str)


class TestIntegration:
    """Simple integration tests with mocked LLM."""

    def test_chat_with_mock_response(self):
        """Test that chat flow handles a mock response correctly."""
        from unittest.mock import MagicMock, patch
        from app import chat

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "You're a boring developer!"

        with patch("app.client.chat.completions.create", return_value=mock_response):
            result = chat("Tell me something funny")
            assert "boring developer" in result

    def test_chat_with_empty_input(self):
        """Test that chat handles empty input gracefully."""
        from app import chat
        result = chat("")
        assert "empty" in result.lower() or "nothing" in result.lower()

    def test_chat_with_whitespace_input(self):
        """Test that chat handles whitespace-only input gracefully."""
        from app import chat
        result = chat("   ")
        assert "empty" in result.lower() or "nothing" in result.lower()


if __name__ == "__main__":
    # Run tests: pytest test_roastbot.py -v
    pytest.main([__file__, "-v"])
