from __future__ import annotations

LETTER_TEMPLATES = frozenset({"classic", "modern", "compact"})
DEFAULT_LETTER_TEMPLATE = "classic"

VOICE_PRESETS = frozenset(
    {
        "direct",
        "founder_operator",
        "product_minded",
        "technically_credible",
    }
)
DEFAULT_VOICE_PRESET = "direct"

# Legacy settings values map to Mission 24 presets.
_LEGACY_VOICE_MAP = {
    "professional": "direct",
    "warm": "product_minded",
    "concise": "technically_credible",
}

VOICE_PROMPT_LINES: dict[str, str] = {
    "direct": (
        "Voice: direct and concise. Lead with outcomes. No corporate filler or buzzword stacking."
    ),
    "founder_operator": (
        "Voice: founder/operator. Bias to ownership, velocity, and building in ambiguity. "
        "Credible operator tone, not investor pitch."
    ),
    "product_minded": (
        "Voice: product-minded. Connect engineering choices to user impact and product bets. "
        "Warm but still evidence-led."
    ),
    "technically_credible": (
        "Voice: technically credible. Name real systems and tradeoffs from the resume. "
        "Depth over hype; no credential inflation."
    ),
}


def normalize_template(raw: str | None) -> str:
    value = (raw or DEFAULT_LETTER_TEMPLATE).strip().casefold()
    return value if value in LETTER_TEMPLATES else DEFAULT_LETTER_TEMPLATE


def normalize_voice_preset(raw: str | None) -> str:
    value = (raw or DEFAULT_VOICE_PRESET).strip().casefold()
    if value in VOICE_PRESETS:
        return value
    return _LEGACY_VOICE_MAP.get(value, DEFAULT_VOICE_PRESET)


def voice_prompt(preset: str) -> str:
    key = normalize_voice_preset(preset)
    return VOICE_PROMPT_LINES[key]
