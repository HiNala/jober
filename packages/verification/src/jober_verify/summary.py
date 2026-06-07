from __future__ import annotations

from typing import Any


def build_human_summary(
    *,
    company: str,
    role: str,
    observations: list[dict[str, Any]],
    readiness_passed: bool,
    skipped_fields: list[str] | None = None,
) -> str:
    filled = [o for o in observations if o.get("status") == "filled"]
    needs_review = [o for o in observations if o.get("status") == "needs_review"]
    failed = [o for o in observations if o.get("status") == "failed"]
    uploads = [
        o
        for o in filled
        if (o.get("mapped_profile_field") or "") in ("resume_upload", "cover_letter_upload")
        or (o.get("field_type") or "").lower() == "file"
    ]

    lines = [
        f"Applying to **{role}** at **{company}**.",
        f"Filled {len(filled)} field(s)"
        + (f" including {len(uploads)} upload(s)" if uploads else "")
        + ".",
    ]
    if needs_review:
        labels = ", ".join(
            (o.get("label") or o.get("field_key") or "?") for o in needs_review[:5]
        )
        lines.append(f"{len(needs_review)} field(s) flagged for review: {labels}.")
    if failed:
        lines.append(f"{len(failed)} field(s) failed to fill — review before submitting.")
    if skipped_fields:
        lines.append(f"Skipped: {', '.join(skipped_fields)}.")
    lines.append(
        "Form readiness: PASSED — safe to review and submit."
        if readiness_passed
        else "Form readiness: FAILED — resolve blockers before submitting."
    )
    return " ".join(lines)
