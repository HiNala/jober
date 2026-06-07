from __future__ import annotations

import ast
import signal
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol


class SandboxActions(Protocol):
    def click_by_role(self, role: str, *, name: str | None = None) -> None: ...
    def click_by_text(self, text: str) -> None: ...
    def fill_by_label(self, label: str, value: str) -> None: ...
    def select_by_label(self, label: str, value: str) -> None: ...
    def check_by_label(self, label: str, *, checked: bool = True) -> None: ...
    def upload_file(self, control: str, file_path: str) -> None: ...
    def wait_for_network_idle(self) -> None: ...
    def screenshot(self) -> bytes: ...
    def record_observation(self, event_type: str, message: str) -> None: ...
    def request_human_checkpoint(self, reason: str) -> None: ...


ALLOWED_ACTION_METHODS = frozenset(
    {
        "click_by_role",
        "click_by_text",
        "fill_by_label",
        "select_by_label",
        "check_by_label",
        "upload_file",
        "wait_for_network_idle",
        "screenshot",
        "record_observation",
        "request_human_checkpoint",
    }
)

FORBIDDEN_NAMES = frozenset(
    {
        "open",
        "exec",
        "eval",
        "compile",
        "__import__",
        "importlib",
        "os",
        "sys",
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "pathlib",
        "shutil",
    }
)


class SandboxViolation(Exception):
    pass


@dataclass
class SnippetRunLog:
    intent: str
    calls: list[str] = field(default_factory=list)


def validate_snippet(source: str) -> None:
    try:
        tree = ast.parse(source, mode="exec")
    except SyntaxError as exc:
        raise SandboxViolation(f"invalid syntax: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom):
            raise SandboxViolation("imports are not allowed in sandbox snippets")
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                raise SandboxViolation("dunder attribute access is not allowed")
            if isinstance(node.value, ast.Name) and node.value.id in FORBIDDEN_NAMES:
                raise SandboxViolation(f"forbidden name: {node.value.id}")
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise SandboxViolation(f"forbidden name: {node.id}")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in FORBIDDEN_NAMES:
                raise SandboxViolation(f"forbidden call: {func.id}")
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id != "actions":
                    raise SandboxViolation("only actions.* calls are allowed")
                if func.attr not in ALLOWED_ACTION_METHODS:
                    raise SandboxViolation(f"action not allowed: {func.attr}")


class _LoggingActionsProxy:
    def __init__(self, actions: SandboxActions, log: SnippetRunLog) -> None:
        self._actions = actions
        self._log = log

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if name not in ALLOWED_ACTION_METHODS:
            raise SandboxViolation(f"action not allowed: {name}")

        def _wrapped(*args: object, **kwargs: object) -> Any:
            self._log.calls.append(f"{name}({args!r}, {kwargs!r})")
            return getattr(self._actions, name)(*args, **kwargs)

        return _wrapped


@contextmanager
def _time_limit(seconds: float):
    if not hasattr(signal, "SIGALRM"):
        yield
        return

    def _handler(_signum: int, _frame: object) -> None:
        raise SandboxViolation("snippet timed out")

    previous = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def run_sandboxed_snippet(
    actions: SandboxActions,
    source: str,
    *,
    intent: str,
    timeout_sec: float = 5.0,
) -> SnippetRunLog:
    validate_snippet(source)
    log = SnippetRunLog(intent=intent)
    proxy = _LoggingActionsProxy(actions, log)
    namespace: dict[str, Any] = {"actions": proxy}
    compiled = compile(source, "<sandbox_snippet>", "exec")
    with _time_limit(timeout_sec):
        exec(compiled, namespace, namespace)  # noqa: S102 — sandboxed AST-validated snippet
    return log
