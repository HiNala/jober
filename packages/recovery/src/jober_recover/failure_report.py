from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jober_recover.taxonomy import FailureClass, is_human_only


@dataclass(frozen=True)
class FailureReport:
    job_target_id: str
    company: str
    role: str
    apply_url: str | None
    failed_step: str
    failure_class: str
    inferred_reason: str
    recommended_manual_action: str
    safe_to_retry: bool
    attempt_count: int
    screenshot_object_key: str | None = None
    trace_object_key: str | None = None
    dom_snapshot_object_key: str | None = None
    attempted_actions: list[str] = field(default_factory=list)
    self_assessments: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_target_id": self.job_target_id,
            "company": self.company,
            "role": self.role,
            "apply_url": self.apply_url,
            "failed_step": self.failed_step,
            "failure_class": self.failure_class,
            "inferred_reason": self.inferred_reason,
            "recommended_manual_action": self.recommended_manual_action,
            "safe_to_retry": self.safe_to_retry,
            "attempt_count": self.attempt_count,
            "screenshot_object_key": self.screenshot_object_key,
            "trace_object_key": self.trace_object_key,
            "dom_snapshot_object_key": self.dom_snapshot_object_key,
            "attempted_actions": self.attempted_actions,
            "self_assessments": self.self_assessments,
        }


_MANUAL_ACTIONS: dict[FailureClass, str] = {
    FailureClass.SELECTOR: "Open the apply page and fill the flagged field manually; confirm mapping in discovered fields.",
    FailureClass.CAPTCHA: "Complete the CAPTCHA in your browser, then retry from the human checkpoint.",
    FailureClass.LOGIN: "Sign in to the ATS account, then resume the run from the checkpoint.",
    FailureClass.TWO_FACTOR: "Complete 2FA on your device, then resume the run.",
    FailureClass.SENSITIVE_FIELD: "Review sensitive answers in Vault and approve or fill manually.",
    FailureClass.UPLOAD: "Upload resume/cover letter manually via the site file control.",
    FailureClass.VALIDATION: "Fix validation errors shown on the form and resubmit.",
    FailureClass.NAVIGATION: "Verify the apply URL is correct and the site is reachable.",
    FailureClass.UNCERTAIN_SUBMISSION: "Check email or ATS dashboard to confirm whether the application was received.",
}


def build_failure_report(
    *,
    job_target_id: str,
    company: str,
    role: str,
    apply_url: str | None,
    failed_step: str,
    failure_class: FailureClass,
    error_message: str,
    attempt_count: int,
    artifact_keys: dict[str, str | None] | None = None,
    attempted_actions: list[str] | None = None,
    self_assessments: list[dict[str, Any]] | None = None,
) -> FailureReport:
    keys = artifact_keys or {}
    manual = _MANUAL_ACTIONS.get(
        failure_class,
        "Review screenshots and trace, then retry or complete the step manually.",
    )
    safe = not is_human_only(failure_class) and failure_class != FailureClass.UNKNOWN
    return FailureReport(
        job_target_id=job_target_id,
        company=company,
        role=role,
        apply_url=apply_url,
        failed_step=failed_step,
        failure_class=failure_class.value,
        inferred_reason=error_message[:1000],
        recommended_manual_action=manual,
        safe_to_retry=safe,
        attempt_count=attempt_count,
        screenshot_object_key=keys.get("screenshot"),
        trace_object_key=keys.get("trace"),
        dom_snapshot_object_key=keys.get("dom"),
        attempted_actions=attempted_actions or [],
        self_assessments=self_assessments or [],
    )
