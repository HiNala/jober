from jober_verify.submission import SubmissionOutcome, classify_submission


def test_classify_success_confirmation() -> None:
    result = classify_submission(
        html="<div>Application received. Thank you for applying.</div>",
        visible_text="Application received. Thank you for applying.",
        final_url="https://jobs.example.com/thanks",
        before_url="https://jobs.example.com/apply",
    )
    assert result.outcome == SubmissionOutcome.SUCCESS
    assert result.confirmation_text


def test_classify_already_applied() -> None:
    result = classify_submission(
        html="<p>You have already applied for this position.</p>",
        visible_text="You have already applied for this position.",
        final_url="https://jobs.example.com/apply",
        submit_clicked=False,
    )
    assert result.outcome == SubmissionOutcome.ALREADY_APPLIED


def test_classify_uncertain_email_followup() -> None:
    result = classify_submission(
        html="<p>Your request is being processed. Please check your email.</p>",
        visible_text="Your request is being processed. Please check your email.",
        final_url="https://jobs.example.com/apply",
        before_url="https://jobs.example.com/apply",
    )
    assert result.outcome == SubmissionOutcome.UNCERTAIN
