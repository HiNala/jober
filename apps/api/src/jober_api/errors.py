from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from jober_api.privacy.logging import safe_log

CORRELATION_ID_HEADER = "X-Correlation-Id"

# Stable codes for clients that branch (web mapper, run console).
CODE_DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
CODE_LLM_BUDGET_EXCEEDED = "llm_budget_exceeded"
CODE_HUMAN_CHECKPOINT_REQUIRED = "human_checkpoint_required"
CODE_VERIFICATION_BLOCKED = "verification_blocked"
CODE_CHECKPOINT_ALREADY_RESOLVED = "checkpoint_already_resolved"

INTERNAL_ERROR_MESSAGE = "Internal server error"
DEPENDENCY_UNAVAILABLE_MESSAGE = (
    "A required service is temporarily unavailable. Try again shortly."
)

# Traceback-shaped leaks only — avoid matching benign client messages ("File is not a zip file").
_LEAK_MARKERS = ("traceback", 'file "', "line ", "sqlalchemy", "asyncpg")


def error_detail(
    message: str,
    *,
    code: str | None = None,
    **extra: object,
) -> str | dict[str, object]:
    """Build HTTPException detail — string or dict with optional `code`."""
    if code is None and not extra:
        return message
    payload: dict[str, object] = {"message": message}
    if code is not None:
        payload["code"] = code
    payload.update(extra)
    return payload


def get_correlation_id(request: Request) -> str:
    stored = getattr(request.state, "correlation_id", None)
    if isinstance(stored, str) and stored:
        return stored
    return str(uuid.uuid4())


def is_dependency_unavailable(exc: BaseException) -> bool:
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return True
    name = type(exc).__name__
    if "Connection" in name or "Timeout" in name:
        return True
    module = getattr(type(exc), "__module__", "") or ""
    if module.startswith("redis") and "Error" in name:
        return True
    return module.startswith("urllib3") or module.startswith("minio")


def dependency_unavailable_http(request: Request) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=error_detail(
            DEPENDENCY_UNAVAILABLE_MESSAGE,
            code=CODE_DEPENDENCY_UNAVAILABLE,
        ),
    )


def budget_exceeded_http(message: str | None = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail=error_detail(
            message or "LLM monthly budget exceeded",
            code=CODE_LLM_BUDGET_EXCEEDED,
        ),
    )


def _response_headers(correlation_id: str) -> dict[str, str]:
    return {CORRELATION_ID_HEADER: correlation_id}


def _envelope(
    *,
    detail: object,
    correlation_id: str,
    code: str | None = None,
) -> dict[str, object]:
    body: dict[str, object] = {"detail": detail, "correlation_id": correlation_id}
    if code is not None:
        body["code"] = code
    return body


def _code_from_detail(detail: object) -> str | None:
    if isinstance(detail, dict):
        raw = detail.get("code")
        if isinstance(raw, str) and raw:
            return raw
    return None


def _assert_no_leak(body: dict[str, object]) -> None:
    text = str(body).lower()
    for marker in _LEAK_MARKERS:
        if marker in text:
            msg = f"error body may leak internals: found {marker!r}"
            raise AssertionError(msg)


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    correlation_id = get_correlation_id(request)
    code = _code_from_detail(exc.detail)
    content = _envelope(detail=exc.detail, correlation_id=correlation_id, code=code)
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=_response_headers(correlation_id),
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc
    correlation_id = get_correlation_id(request)
    content = _envelope(detail=exc.errors(), correlation_id=correlation_id)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content,
        headers=_response_headers(correlation_id),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = get_correlation_id(request)
    safe_log(
        logging.ERROR,
        "unhandled_exception",
        correlation_id=correlation_id,
        exc_type=type(exc).__name__,
    )
    content = _envelope(detail=INTERNAL_ERROR_MESSAGE, correlation_id=correlation_id)
    _assert_no_leak(content)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
        headers=_response_headers(correlation_id),
    )


class CorrelationIdMiddleware:
    """Pure ASGI middleware — avoids BaseHTTPMiddleware event-loop clashes in pytest-asyncio."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        correlation_id = str(uuid.uuid4())
        for name, value in scope.get("headers", ()):
            if name.lower() == b"x-correlation-id":
                decoded = value.decode("latin-1").strip()
                if decoded:
                    correlation_id = decoded
                break

        scope.setdefault("state", {})["correlation_id"] = correlation_id

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-correlation-id", correlation_id.encode("latin-1")))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)


def register_exception_handlers(app: FastAPI) -> None:
    # Starlette routing 404s use starlette.exceptions.HTTPException — register both aliases.
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

