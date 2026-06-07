from __future__ import annotations

import json
import re
from typing import Any


def flatten_accessibility_tree(tree: dict[str, Any] | list[Any] | None) -> str:
    """Collect role:name lines from a Playwright accessibility snapshot."""
    if tree is None:
        return ""
    lines: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            role = str(node.get("role", "")).strip()
            name = str(node.get("name", "")).strip()
            if role and name:
                lines.append(f"{role}: {name}")
            for child in node.get("children", []) or []:
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(tree)
    return "\n".join(lines)


def parse_accessibility_json(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    return flatten_accessibility_tree(data)


def extract_visible_text_from_html(html: str) -> str:
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
