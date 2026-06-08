from jober_api.models.job_target import JobTarget
from jober_api.services.ats_guess import guess_ats, needs_apply_url


def serialize_job_target(job: JobTarget) -> dict[str, object]:
    url = job.direct_apply_url or job.company_careers_url
    fit_score: float | None = None
    if isinstance(job.extracted_job_profile, dict):
        raw_fit = job.extracted_job_profile.get("fit_score")
        if isinstance(raw_fit, (int, float)):
            fit_score = float(raw_fit)
    return {
        "id": str(job.id),
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "rank": job.rank,
        "priority": job.priority,
        "company": job.company,
        "role": job.role,
        "fit_lane": job.fit_lane,
        "stage_signal": job.stage_signal,
        "location_work_style": job.location_work_style,
        "why_fit": job.why_fit,
        "cover_letter_hook": job.cover_letter_hook,
        "public_contact": job.public_contact,
        "direct_apply_url": job.direct_apply_url,
        "company_careers_url": job.company_careers_url,
        "source_note": job.source_note,
        "verified_date": job.verified_date.isoformat() if job.verified_date else None,
        "status": job.status.value,
        "applied_date": job.applied_date.isoformat() if job.applied_date else None,
        "follow_up_date": job.follow_up_date.isoformat() if job.follow_up_date else None,
        "notes": job.notes,
        "import_id": job.import_id,
        "ats_guess": guess_ats(url),
        "needs_url": needs_apply_url(job.direct_apply_url, job.company_careers_url),
        "fit_score": fit_score,
    }
