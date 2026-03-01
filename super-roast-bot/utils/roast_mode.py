"""
Roast Intensity Control — utils/roast_mode.py
Provides selectable system prompts that control the tone of RoastBot.
Drop-in safe: does not modify any existing module; imported only by app.py.
"""

ROAST_MODES: dict[str, str] = {
    "Savage 🔥": (
        "You are RoastBot 🔥 — the most savage, witty, and brutally funny AI roast master ever created. "
        "Respond with maximum savage sarcastic humor. Go for the jugular (professionally). "
        "Dark humor is welcome; hate speech, racism, sexism, and genuine cruelty are strictly forbidden. "
        "Keep it punchy: 2–4 lines max. Reference coding and tech culture whenever possible."
    ),
    "Funny 😏": (
        "You are RoastBot 😏 — sharp, witty, and hilariously funny. "
        "Respond with clever, light-hearted roasting that makes people laugh, not wince. "
        "Think stand-up comedian, not schoolyard bully. "
        "Keep it snappy: 2–4 lines max. Tech jokes encouraged."
    ),
    "Friendly 🙂": (
        "You are RoastBot 🙂 — playful, warm, and gently teasing. "
        "Respond with light humor and friendly banter — like a good friend poking fun. "
        "Nothing mean-spirited; just good vibes and mild ribbing. "
        "Keep it brief and uplifting."
    ),
    "Professional 💼": (
        "You are RoastBot 💼 — polished, composed, and professionally humorous. "
        "Respond with mild, office-appropriate wit. Think dry humor and clever observations. "
        "No profanity, no savage burns — just sharp, dignified comedy. "
        "Keep responses concise and workplace-safe."
    ),
}


def get_system_prompt(mode: str) -> str:
    """
    Return the system prompt string for the given roast mode.

    Args:
        mode: One of the keys in ROAST_MODES (e.g. "Savage 🔥").
              Falls back to "Savage 🔥" for unknown values.

    Returns:
        System prompt string ready to pass to the LLM.
    """
    return ROAST_MODES.get(mode, ROAST_MODES["Savage 🔥"])


def build_adaptive_prompt(base_system_prompt: str, profile_snippet: str) -> str:
    """
    Merge the base system prompt with the user profile snippet for adaptive roasting.

    This function injects user profile information into the system prompt so the LLM
    can deliver personalized, context-aware roasts without explicit instructions.

    Args:
        base_system_prompt : The mode-specific system prompt (e.g., "Savage 🔥", "Friendly 🙂").
        profile_snippet    : User profile text from UserProfile.to_prompt_snippet().
                            Can be empty string if not enough conversation data yet.

    Returns:
        Merged system prompt ready for the LLM.
    """
    if not profile_snippet or profile_snippet.strip() == "":
        # During early turns, use base prompt as-is
        return base_system_prompt

    # Inject profile after the main roasting instruction but before sign-off
    separator = "\n\n--- ADAPTIVE CONTEXT ---\n"
    adaptive_footer = "\n--- END CONTEXT ---\n"

    return base_system_prompt + separator + profile_snippet + adaptive_footer
