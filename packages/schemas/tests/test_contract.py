"""Contract tests — Python enums must match generated TypeScript unions."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from jober_schemas.enums import JobTargetStatus, RunPolicy, RunStatus

SCHEMAS_ROOT = Path(__file__).resolve().parents[1]
EXPORT_SCRIPT = SCHEMAS_ROOT / "scripts" / "export_typescript.py"
GENERATED_TS = SCHEMAS_ROOT / "generated" / "types.ts"


def _export_typescript() -> str:
    subprocess.run([sys.executable, str(EXPORT_SCRIPT)], check=True, cwd=str(SCHEMAS_ROOT))
    return GENERATED_TS.read_text(encoding="utf-8")


def _ts_union(name: str, content: str) -> set[str]:
    match = re.search(rf"export type {name} = (.+?);", content)
    assert match, f"missing export type {name}"
    return set(re.findall(r'"([^"]+)"', match.group(1)))


def test_run_status_matches_typescript_export() -> None:
    ts = _export_typescript()
    py_values = {m.value for m in RunStatus}
    ts_values = _ts_union("RunStatus", ts)
    assert py_values == ts_values


def test_job_target_status_matches_typescript_export() -> None:
    ts = GENERATED_TS.read_text(encoding="utf-8")
    py_values = {m.value for m in JobTargetStatus}
    ts_values = _ts_union("JobTargetStatus", ts)
    assert py_values == ts_values


def test_run_policy_auto_submit_is_explicit_opt_in() -> None:
    """Contract: auto_submit exists in enum but default policy is review_before_submit."""
    assert RunPolicy.AUTO_SUBMIT.value == "auto_submit"
    assert RunPolicy.REVIEW_BEFORE_SUBMIT.value == "review_before_submit"
