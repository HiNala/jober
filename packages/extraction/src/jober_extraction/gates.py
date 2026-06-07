from __future__ import annotations

import re
from enum import StrEnum


class GateKind(StrEnum):
    LOGIN = "login"
    CAPTCHA = "captcha"
    TWO_FACTOR = "two_factor"


LOGIN_PATTERNS = (
    re.compile(r"type=[\"']password[\"']", re.I),
    re.compile(r"sign\s*in|log\s*in|authenticate", re.I),
)
CAPTCHA_PATTERNS = (
    re.compile(r"recaptcha|g-recaptcha|hcaptcha|cf-turnstile", re.I),
    re.compile(r"captcha|bot\s*challenge|verify\s*you\s*are\s*human", re.I),
)
TWO_FACTOR_PATTERNS = (
    re.compile(r"two[- ]factor|2fa|verification\s*code|one[- ]time\s*code", re.I),
    re.compile(r"authenticator\s*app", re.I),
)


def detect_access_gates(html: str, visible_text: str) -> list[GateKind]:
    combined = f"{html}\n{visible_text}"
    gates: list[GateKind] = []
    if any(p.search(combined) for p in CAPTCHA_PATTERNS):
        gates.append(GateKind.CAPTCHA)
    if any(p.search(combined) for p in TWO_FACTOR_PATTERNS):
        gates.append(GateKind.TWO_FACTOR)
    if any(p.search(combined) for p in LOGIN_PATTERNS):
        gates.append(GateKind.LOGIN)
    return gates
