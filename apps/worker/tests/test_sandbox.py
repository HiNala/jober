from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from jober_fill.sandbox import SandboxViolation, run_sandboxed_snippet, validate_snippet


@dataclass
class StubActions:
    calls: list[str] = field(default_factory=list)

    def click_by_role(self, role: str, *, name: str | None = None) -> None:
        self.calls.append(f"click_by_role:{role}:{name}")

    def click_by_text(self, text: str) -> None:
        self.calls.append(f"click_by_text:{text}")

    def fill_by_label(self, label: str, value: str) -> None:
        self.calls.append(f"fill_by_label:{label}")

    def select_by_label(self, label: str, value: str) -> None:
        self.calls.append(f"select_by_label:{label}")

    def check_by_label(self, label: str, *, checked: bool = True) -> None:
        self.calls.append(f"check_by_label:{label}")

    def upload_file(self, control: str, file_path: str) -> None:
        self.calls.append(f"upload_file:{control}")

    def wait_for_network_idle(self) -> None:
        self.calls.append("wait")

    def screenshot(self) -> bytes:
        return b"png"

    def record_observation(self, event_type: str, message: str) -> None:
        self.calls.append(f"obs:{event_type}")

    def request_human_checkpoint(self, reason: str) -> None:
        self.calls.append(f"checkpoint:{reason}")


def test_sandbox_allows_typed_actions() -> None:
    actions = StubActions()
    log = run_sandboxed_snippet(
        actions,
        "actions.fill_by_label('Email', 'a@b.com')\nactions.click_by_role('button', name='Next')",
        intent="advance form",
    )
    assert "fill_by_label:Email" in actions.calls
    assert len(log.calls) == 2


@pytest.mark.parametrize(
    "snippet",
    [
        "import os",
        "open('/etc/passwd')",
        "actions.__class__.__bases__[0].__subclasses__()",
        "__import__('os').system('ls')",
    ],
)
def test_sandbox_blocks_malicious_snippet(snippet: str) -> None:
    with pytest.raises(SandboxViolation):
        validate_snippet(snippet)
