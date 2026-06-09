from __future__ import annotations

from typing import Any

# Funnel steps mapped to canonical event names (Mission 26 dashboards consume these).
FUNNEL_STEPS: dict[str, str] = {
    "landing": "page.view",
    "signup_start": "signup.start",
    "signup_complete": "signup.complete",
    "first_list": "list.create",
    "first_run": "run.start",
    "first_submit": "submit.complete",
}

CLIENT_EVENTS: frozenset[str] = frozenset(
    {
        "page.view",
        "signup.start",
        "feature.use",
    }
)

SERVER_EVENTS: frozenset[str] = frozenset(
    {
        "signup.complete",
        "list.create",
        "run.start",
        "submit.complete",
        "letter.generate",
        "run.complete",
    }
)

ALLOWED_PROP_KEYS: dict[str, frozenset[str]] = {
    "page.view": frozenset({"title", "path", "exit"}),
    "signup.start": frozenset(),
    "signup.complete": frozenset({"method"}),
    "list.create": frozenset({"list_id"}),
    "run.start": frozenset({"run_id", "job_target_id"}),
    "run.complete": frozenset({"run_id", "status"}),
    "submit.complete": frozenset({"run_id"}),
    "letter.generate": frozenset({"document_id", "job_target_id"}),
    "feature.use": frozenset({"feature"}),
}

PII_PROP_KEYS: frozenset[str] = frozenset(
    {
        "email",
        "name",
        "phone",
        "address",
        "password",
        "token",
        "ip",
        "ip_address",
    }
)


def is_registered_event(name: str) -> bool:
    return name in ALLOWED_PROP_KEYS


def validate_event(name: str, props: dict[str, Any], *, source: str) -> None:
    if not is_registered_event(name):
        msg = f"Unknown analytics event: {name}"
        raise ValueError(msg)
    if source == "client" and name not in CLIENT_EVENTS:
        msg = f"Event {name} is server-only"
        raise ValueError(msg)
    if source == "server" and name not in SERVER_EVENTS:
        msg = f"Event {name} is not allowed from server emitter"
        raise ValueError(msg)
    allowed = ALLOWED_PROP_KEYS.get(name, frozenset())
    for key in props:
        key_lower = key.lower()
        if key_lower in PII_PROP_KEYS:
            msg = f"PII key not allowed in analytics props: {key}"
            raise ValueError(msg)
        if key not in allowed:
            msg = f"Unexpected prop '{key}' for event {name}"
            raise ValueError(msg)


def sanitize_props(name: str, props: dict[str, Any]) -> dict[str, Any]:
    allowed = ALLOWED_PROP_KEYS.get(name, frozenset())
    return {k: v for k, v in props.items() if k in allowed}
