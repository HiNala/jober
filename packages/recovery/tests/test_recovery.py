from jober_recover.budget import AttemptBudget
from jober_recover.circuit_breaker import CircuitBreaker
from jober_recover.failure_report import build_failure_report
from jober_recover.strategy import propose_recovery_strategy
from jober_recover.taxonomy import FailureClass, classify_failure


def test_classify_selector_failure() -> None:
    assert classify_failure(step="fill_form", error_message="Could not resolve #legacy-email") == (
        FailureClass.SELECTOR
    )


def test_budget_blocks_captcha_retry() -> None:
    budget = AttemptBudget()
    assert budget.can_retry(1, failure_class=FailureClass.CAPTCHA) is False


def test_selector_recovery_strategy_escalates() -> None:
    first = propose_recovery_strategy(FailureClass.SELECTOR, attempt_index=1)
    second = propose_recovery_strategy(FailureClass.SELECTOR, attempt_index=2)
    assert first.locator_mode == "css"
    assert second.locator_mode == "label"


def test_circuit_breaker_trips() -> None:
    breaker = CircuitBreaker(threshold=3)
    for _ in range(3):
        state = breaker.record("greenhouse", FailureClass.SELECTOR)
    assert state.tripped is True
    assert len(breaker.active_alerts()) == 1


def test_failure_report_safe_to_retry() -> None:
    report = build_failure_report(
        job_target_id="id",
        company="Acme",
        role="Eng",
        apply_url="https://jobs.example.com",
        failed_step="fill_form",
        failure_class=FailureClass.SELECTOR,
        error_message="locator timeout",
        attempt_count=4,
    )
    assert report.safe_to_retry is True
    assert report.recommended_manual_action
