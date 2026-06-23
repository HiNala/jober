from __future__ import annotations

import json
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import text

from jober_worker.db import get_sync_session
from jober_worker.storage import ObjectStorage

SENSITIVE_KEYS = frozenset(
    {
        "work_authorization",
        "sponsorship_needed",
        "disability",
        "veteran_status",
        "race_ethnicity",
        "gender",
    }
)


@dataclass(frozen=True)
class FillObservationRow:
    id: uuid.UUID
    field_key: str
    label: str | None
    field_type: str | None
    mapped_profile_field: str | None
    status: str
    evidence: dict[str, Any] | None


@dataclass
class FillContext:
    profile_values: dict[str, Any]
    observations: list[FillObservationRow]
    observation_attempt_id: uuid.UUID | None
    resume_path: Path | None
    cover_letter_path: Path | None
    temp_dir: tempfile.TemporaryDirectory[str]


def load_fill_context(job_target_id: uuid.UUID, _fill_attempt_id: uuid.UUID) -> FillContext:
    storage = ObjectStorage()
    temp = tempfile.TemporaryDirectory(prefix="jober-fill-")
    base = Path(temp.name)
    profile_values: dict[str, Any] = {}
    resume_path: Path | None = None
    cover_path: Path | None = None

    with get_sync_session() as session:
        profile = session.execute(
            text(
                """
                SELECT p.name, p.email, p.phone, p.location, p.current_title, p.links,
                       p.relocation_pref, p.onsite_pref, p.hybrid_pref, p.notice_period,
                       p.salary_prefs, p.sensitive_eeo_answers, p.field_consent
                FROM user_profiles p
                JOIN job_targets j ON j.id = :job_id AND j.tenant_id = p.tenant_id
                ORDER BY p.updated_at DESC NULLS LAST, p.created_at DESC
                LIMIT 1
                """
            ),
            {"job_id": str(job_target_id)},
        ).mappings().first()

        if profile:
            for key in (
                "name",
                "email",
                "phone",
                "location",
                "current_title",
                "links",
                "relocation_pref",
                "onsite_pref",
                "hybrid_pref",
                "notice_period",
                "salary_prefs",
            ):
                val = profile.get(key)
                if val not in (None, ""):
                    profile_values[key] = val
            _merge_sensitive(profile, profile_values)

        obs_rows = session.execute(
            text(
                """
                SELECT f.id, f.field_key, f.label, f.field_type, f.mapped_profile_field,
                       f.status, f.evidence, f.attempt_id
                FROM form_field_observations f
                JOIN application_attempts a ON f.attempt_id = a.id
                JOIN application_runs r ON a.run_id = r.id
                WHERE r.job_target_id = :job_id
                ORDER BY r.created_at DESC, f.field_key
                """
            ),
            {"job_id": str(job_target_id)},
        ).mappings().all()

        resume = session.execute(
            text(
                """
                SELECT r.id, r.object_key, r.original_filename
                FROM resume_assets r
                JOIN job_targets j ON j.id = :job_id AND j.tenant_id = r.tenant_id
                WHERE r.is_active = true
                ORDER BY r.created_at DESC
                LIMIT 1
                """
            ),
            {"job_id": str(job_target_id)},
        ).mappings().first()

        cover = session.execute(
            text(
                """
                SELECT object_key_pdf
                FROM generated_documents
                WHERE job_target_id = :job_id AND document_type = 'cover_letter'
                ORDER BY created_at DESC
                LIMIT 1
                """
            ),
            {"job_id": str(job_target_id)},
        ).mappings().first()

    if resume and resume.get("object_key"):
        resume_path = base / str(resume.get("original_filename") or "resume.pdf")
        resume_path.write_bytes(storage.get_bytes(str(resume["object_key"])))

    if cover and cover.get("object_key_pdf"):
        cover_path = base / "cover_letter.pdf"
        cover_path.write_bytes(storage.get_bytes(str(cover["object_key_pdf"])))

    observations = [
        FillObservationRow(
            id=uuid.UUID(str(row["id"])),
            field_key=str(row["field_key"]),
            label=row.get("label"),
            field_type=row.get("field_type"),
            mapped_profile_field=row.get("mapped_profile_field"),
            status=str(row["status"]),
            evidence=row.get("evidence") if isinstance(row.get("evidence"), dict) else None,
        )
        for row in obs_rows
    ]

    latest_attempt: uuid.UUID | None = None
    if obs_rows:
        latest_attempt = uuid.UUID(str(obs_rows[0]["attempt_id"]))
        obs_rows = [row for row in obs_rows if str(row["attempt_id"]) == str(latest_attempt)]

    return FillContext(
        profile_values=profile_values,
        observations=observations,
        observation_attempt_id=latest_attempt,
        resume_path=resume_path,
        cover_letter_path=cover_path,
        temp_dir=temp,
    )


def _merge_sensitive(profile: Any, profile_values: dict[str, Any]) -> None:
    from cryptography.fernet import Fernet, InvalidToken

    from jober_worker.config import settings

    encrypted = profile.get("sensitive_eeo_answers")
    consent_flags = profile.get("field_consent") or {}
    if not encrypted or not settings.vault_encryption_key:
        return
    try:
        fernet = Fernet(settings.vault_encryption_key.encode())
        raw = fernet.decrypt(str(encrypted).encode())
        answers = json.loads(raw.decode())
    except (InvalidToken, json.JSONDecodeError, ValueError):
        return
    if not isinstance(answers, dict):
        return
    for key in SENSITIVE_KEYS:
        flags = consent_flags.get(key, {}) if isinstance(consent_flags, dict) else {}
        if isinstance(flags, dict) and flags.get("never_autofill"):
            continue
        if isinstance(flags, dict) and flags.get("consent") and answers.get(key):
            profile_values[key] = answers[key]


def is_sensitive_observation(obs: FillObservationRow) -> bool:
    mapped = obs.mapped_profile_field
    return mapped in SENSITIVE_KEYS or (
        isinstance(obs.evidence, dict) and bool(obs.evidence.get("sensitive"))
    )
