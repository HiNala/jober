from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text

from jober_worker.db import get_sync_session


def load_extraction_context(job_target_id: uuid.UUID) -> dict[str, Any]:
    with get_sync_session() as session:
        row = session.execute(
            text(
                """
                SELECT j.company, r.skills_index
                FROM job_targets j
                LEFT JOIN resume_assets r ON r.is_active = true
                WHERE j.id = :job_id
                ORDER BY r.created_at DESC NULLS LAST
                LIMIT 1
                """
            ),
            {"job_id": str(job_target_id)},
        ).mappings().first()
    if row is None:
        return {"company_hint": "", "resume_skills": []}
    skills_index = row.get("skills_index")
    skills: list[str] = []
    if isinstance(skills_index, dict) and isinstance(skills_index.get("skills"), list):
        skills = [str(s) for s in skills_index["skills"]]
    elif isinstance(skills_index, str):
        try:
            parsed = json.loads(skills_index)
            if isinstance(parsed, dict) and isinstance(parsed.get("skills"), list):
                skills = [str(s) for s in parsed["skills"]]
        except json.JSONDecodeError:
            pass
    return {
        "company_hint": str(row.get("company") or ""),
        "resume_skills": skills,
    }
