from __future__ import annotations

import re
from enum import StrEnum


class FailureClass(StrEnum):
    NAVIGATION = "navigation"
    PLATFORM_DETECTION = "platform_detection"
    FORM_DISCOVERY = "form_discovery"
    SELECTOR = "selector"
    UPLOAD = "upload"
    VALIDATION = "validation"
    UNCERTAIN_SUBMISSION = "uncertain_submission"
    CAPTCHA = "captcha"
    LOGIN = "login"
    TWO_FACTOR = "two_factor"
    SENSITIVE_FIELD = "sensitive_field"
    UNKNOWN = "unknown"


_HUMAN_ONLY = frozenset(
    {
        FailureClass.CAPTCHA,
        FailureClass.LOGIN,
        FailureClass.TWO_FACTOR,
        FailureClass.SENSITIVE_FIELD,
    }
)


def is_human_only(failure_class: FailureClass) -> bool:
    return failure_class in _HUMAN_ONLY


def classify_failure(
    *,
    step: str,
    error_message: str,
    gate: str | None = None,
) -> FailureClass:
    if gate:
        gate_map = {
            "captcha": FailureClass.CAPTCHA,
            "login": FailureClass.LOGIN,
            "two_factor": FailureClass.TWO_FACTOR,
            "sensitive_field": FailureClass.SENSITIVE_FIELD,
        }
        if gate in gate_map:
            return gate_map[gate]

    text = f"{step} {error_message}".lower()
    patterns: list[tuple[FailureClass, tuple[str, ...]]] = [
        (FailureClass.NAVIGATION, (r"navigation", r"timeout", r"net::err", r"page\.goto")),
        (FailureClass.PLATFORM_DETECTION, (r"platform", r"ats detection")),
        (FailureClass.FORM_DISCOVERY, (r"discover", r"scan.*form", r"no fields")),
        (FailureClass.SELECTOR, (r"selector", r"locator", r"could not resolve", r"#legacy")),
        (FailureClass.UPLOAD, (r"upload", r"set_input_files", r"file chooser")),
        (FailureClass.VALIDATION, (r"validation", r"required", r"invalid field")),
        (FailureClass.UNCERTAIN_SUBMISSION, (r"uncertain", r"confirmation unclear")),
        (FailureClass.CAPTCHA, (r"captcha", r"bot challenge", r"recaptcha")),
        (FailureClass.LOGIN, (r"\blogin\b", r"sign in")),
        (FailureClass.TWO_FACTOR, (r"2fa", r"two.factor", r"mfa")),
        (FailureClass.SENSITIVE_FIELD, (r"sensitive", r"eeo", r"work authorization")),
    ]
    for failure_class, pats in patterns:
        if any(re.search(p, text) for p in pats):
            return failure_class
    return FailureClass.UNKNOWN
