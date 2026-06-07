from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class ReadinessPage(Protocol):
    def evaluate(self, expression: str) -> Any: ...


@dataclass(frozen=True)
class ReadinessCheck:
    check_id: str
    passed: bool
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReadinessReport:
    passed: bool
    checks: list[ReadinessCheck]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [
                {
                    "check_id": c.check_id,
                    "passed": c.passed,
                    "reason": c.reason,
                    "evidence": c.evidence,
                }
                for c in self.checks
            ],
        }


_READINESS_JS = """
() => {
  const inputs = [...document.querySelectorAll('input, select, textarea')];
  const emptyRequired = [];
  for (const el of inputs) {
    if (!el.required && !el.hasAttribute('aria-required')) continue;
    const label = el.labels?.[0]?.textContent?.trim() || el.name || el.id || 'field';
    if (el.type === 'file') {
      if (!el.files || el.files.length === 0) emptyRequired.push(label);
      continue;
    }
    const value = el.type === 'checkbox' ? el.checked : (el.value || '').trim();
    if (!value) emptyRequired.push(label);
  }

  const validationErrors = [];
  const errorNodes = document.querySelectorAll(
    '.error, .field-error, [role="alert"], .validation-error, .invalid-feedback'
  );
  for (const node of errorNodes) {
    const text = (node.textContent || '').trim();
    if (!text) continue;
    const style = window.getComputedStyle(node);
    if (style.display === 'none' || style.visibility === 'hidden') continue;
    validationErrors.push(text.slice(0, 200));
  }
  const invalidInputs = [...document.querySelectorAll(':invalid')].filter((el) => {
    const style = window.getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden';
  });
  for (const el of invalidInputs) {
    const label =
      el.labels?.[0]?.textContent?.trim() ||
      el.getAttribute('aria-label') ||
      el.name ||
      el.id ||
      'field';
    if (label && !label.includes('[object')) {
      validationErrors.push(`Invalid: ${label}`);
    }
  }

  const submitCandidates = [
    ...document.querySelectorAll('button[type="submit"], input[type="submit"]'),
    ...document.querySelectorAll('button:not([type])'),
    ...[...document.querySelectorAll('button[type="button"]')].filter((el) =>
      /submit|apply/i.test((el.textContent || '').trim())
    ),
  ];
  let submit = submitCandidates.find((el) => {
    const style = window.getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden';
  }) || null;

  const submitState = submit
    ? {
        found: true,
        disabled: submit.disabled || submit.getAttribute('aria-disabled') === 'true',
        text: (submit.textContent || submit.value || '').trim().slice(0, 120),
        blocking: submit.getAttribute('title') || submit.getAttribute('data-disabled-reason') || null,
      }
    : { found: false, disabled: true, text: '', blocking: 'No submit control visible' };

  const fileInputs = [...document.querySelectorAll('input[type="file"]')].map((el) => ({
    name: el.name || el.id || 'file',
    label: el.labels?.[0]?.textContent?.trim() || el.name || el.id || 'file',
    attached: !!(el.files && el.files.length > 0),
    file_count: el.files ? el.files.length : 0,
  }));

  return { emptyRequired, validationErrors, submitState, fileInputs };
}
"""


def evaluate_readiness(
    page: ReadinessPage,
    *,
    require_uploads: bool = True,
) -> ReadinessReport:
    raw = page.evaluate(_READINESS_JS)
    checks: list[ReadinessCheck] = []

    empty_required: list[str] = raw.get("emptyRequired", [])
    checks.append(
        ReadinessCheck(
            check_id="required_fields",
            passed=len(empty_required) == 0,
            reason=(
                "All required fields have values"
                if not empty_required
                else f"Missing required: {', '.join(empty_required)}"
            ),
            evidence={"missing": empty_required},
        )
    )

    validation_errors: list[str] = raw.get("validationErrors", [])
    checks.append(
        ReadinessCheck(
            check_id="validation_errors",
            passed=len(validation_errors) == 0,
            reason=(
                "No visible validation errors"
                if not validation_errors
                else f"Validation blocking submit: {validation_errors[0]}"
            ),
            evidence={"errors": validation_errors[:10]},
        )
    )

    submit_state: dict[str, Any] = raw.get("submitState", {})
    submit_found = bool(submit_state.get("found"))
    submit_disabled = bool(submit_state.get("disabled"))
    blocking = submit_state.get("blocking")
    if submit_disabled and not blocking and submit_found:
        blocking = "Submit control is disabled"
    checks.append(
        ReadinessCheck(
            check_id="submit_enabled",
            passed=submit_found and not submit_disabled,
            reason=(
                "Submit control is enabled"
                if submit_found and not submit_disabled
                else str(blocking or "Submit control missing or disabled")
            ),
            evidence={"submit": submit_state},
        )
    )

    file_inputs: list[dict[str, Any]] = raw.get("fileInputs", [])
    unattached = [f["label"] for f in file_inputs if not f.get("attached")]
    if require_uploads and file_inputs:
        uploads_ok = len(unattached) == 0
        checks.append(
            ReadinessCheck(
                check_id="uploads_attached",
                passed=uploads_ok,
                reason=(
                    "All file inputs have attachments"
                    if uploads_ok
                    else f"Missing uploads: {', '.join(unattached)}"
                ),
                evidence={"file_inputs": file_inputs},
            )
        )
    elif require_uploads:
        checks.append(
            ReadinessCheck(
                check_id="uploads_attached",
                passed=True,
                reason="No file inputs on form",
                evidence={"file_inputs": []},
            )
        )

    passed = all(c.passed for c in checks)
    return ReadinessReport(passed=passed, checks=checks)
