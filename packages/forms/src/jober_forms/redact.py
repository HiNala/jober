from __future__ import annotations


def redact_value(value: object | None, *, field_type: str | None = None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if field_type == "email" and "@" in text:
        local, _, domain = text.partition("@")
        masked = (local[:1] + "***") if local else "***"
        return f"{masked}@{domain}"
    if field_type in ("tel", "phone") or (field_type == "text" and text.replace("-", "").isdigit()):
        digits = "".join(c for c in text if c.isdigit())
        if len(digits) >= 4:
            return f"***-***-{digits[-4:]}"
    if len(text) <= 4:
        return "***"
    return f"{text[:2]}…{text[-1]}"
