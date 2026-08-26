"""
llm_client.py
-------------
Thin wrapper around the Anthropic API so the rest of the app only calls
`generate_json()` and doesn't care which model/provider is behind it.

Requires an ANTHROPIC_API_KEY environment variable.
"""

import os
import json
import re
import anthropic

MODEL = "claude-sonnet-4-6"


def _client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Get a key from console.anthropic.com and set it before running the app."
        )
    return anthropic.Anthropic(api_key=api_key)


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def generate_json(prompt: str) -> dict:
    """Calls Claude with the given prompt and parses the JSON response."""
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    cleaned = _strip_code_fences(raw_text)
    return json.loads(cleaned)
