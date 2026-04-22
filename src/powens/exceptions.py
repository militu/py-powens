"""Typed exception hierarchy for py-powens.

All exceptions raised by the SDK derive from :class:`PowensError`, which
allows callers to either catch everything SDK-related or narrow down on a
specific failure mode (auth, rate limit, conflict, parsing, etc.).

Powens returns every API error using a common envelope:
``{ code, description, message, request_id }``. See
https://docs.powens.com/api-reference/overview/errors for the full
specification. The envelope is parsed onto every :class:`PowensHTTPError`
subclass, and the Powens documentation recommends branching on
``error_code`` rather than on the HTTP status.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class PowensErrorCode(StrEnum):
    """Known Powens error codes.

    Powens documents this list as open: unknown values must fall back to a
    generic case. Callers receive the raw string on
    :attr:`PowensHTTPError.error_code` and can compare against this enum
    using ``==`` thanks to ``StrEnum``; unknown values are preserved as
    plain strings.
    """

    # Documented common error codes
    # https://docs.powens.com/api-reference/overview/errors#common-error-codes
    CONNECTION_LOCKED = "connectionLocked"
    MISSING_PARAMETER = "missingParameter"
    INVALID_VALUE = "invalidValue"
    METHOD_NOT_ALLOWED = "methodNotAllowed"
    BUG = "bug"
    # Additional codes referenced in endpoint documentation
    WRONG_PASS = "wrongPass"
    NO_ACCOUNT = "noAccount"


class PowensError(Exception):
    """Base class for every exception raised by the SDK."""


class PowensHTTPError(PowensError):
    """Raised when the Powens API returns an unsuccessful HTTP response.

    The response body is parsed according to the Powens error envelope
    specification; individual fields are exposed as attributes and the raw
    body is preserved for callers that need it.

    Attributes:
        status_code: HTTP status code returned by the Powens API.
        response_body: Raw response body (parsed as JSON when possible,
            otherwise the raw string).
        request_method: The HTTP method used for the request.
        request_url: The URL that was requested.
        error_code: Parsed ``code`` field from the Powens error envelope.
            See :class:`PowensErrorCode` for known values; the attribute
            holds a ``str`` to tolerate future codes.
        error_description: Parsed ``description`` (technical, not for
            end-user display).
        error_message: Parsed ``message`` (optional, suitable for end-user
            display).
        request_id: Parsed ``request_id`` (useful for audit / support).
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: Any = None,
        request_method: str | None = None,
        request_url: str | None = None,
        error_code: str | None = None,
        error_description: str | None = None,
        error_message: str | None = None,
        request_id: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_method = request_method
        self.request_url = request_url
        self.error_code = error_code
        self.error_description = error_description
        self.error_message = error_message
        self.request_id = request_id


class PowensBadRequestError(PowensHTTPError):
    """Raised for 400 Bad Request responses."""


class PowensAuthError(PowensHTTPError):
    """Raised for authentication/authorization failures (401, 403)."""


class PowensNotFoundError(PowensHTTPError):
    """Raised for 404 Not Found responses."""


class PowensConflictError(PowensHTTPError):
    """Raised for 409 Conflict responses.

    Powens uses 409 to signal conflicting state, e.g. when requesting a
    ``/webauth-url`` while the connection is already up to date.
    """


class PowensRateLimitError(PowensHTTPError):
    """Raised for 429 Too Many Requests responses.

    Attributes:
        retry_after: Value of the ``Retry-After`` header, in seconds, if
            provided by the server.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 429,
        response_body: Any = None,
        request_method: str | None = None,
        request_url: str | None = None,
        error_code: str | None = None,
        error_description: str | None = None,
        error_message: str | None = None,
        request_id: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            response_body=response_body,
            request_method=request_method,
            request_url=request_url,
            error_code=error_code,
            error_description=error_description,
            error_message=error_message,
            request_id=request_id,
        )
        self.retry_after = retry_after


class PowensServerError(PowensHTTPError):
    """Raised for 500 Internal Server Error responses."""


class PowensServiceUnavailableError(PowensHTTPError):
    """Raised for 503 Service Unavailable responses.

    Powens documents 503 specifically as "API temporarily down for
    maintenance".
    """


class PowensConnectionError(PowensError):
    """Raised when the SDK fails to reach the Powens API (network error)."""


class PowensSerializationError(PowensError):
    """Raised when a response body cannot be parsed into the expected model."""


class PowensCircuitOpenError(PowensError):
    """Raised when the injected circuit breaker short-circuits a call."""


def parse_error_envelope(body: Any) -> tuple[str | None, str | None, str | None, int | None]:
    """Extract ``(code, description, message, request_id)`` from a Powens error body.

    Returns a 4-tuple of optionals. Missing fields return ``None``. Non-dict
    bodies (strings, lists, numbers) return four ``None`` values: the body
    is then preserved on :attr:`PowensHTTPError.response_body` for the
    caller to inspect.
    """
    if not isinstance(body, dict):
        return None, None, None, None
    code = body.get("code")
    description = body.get("description")
    message = body.get("message")
    request_id = body.get("request_id")

    code_str = code if isinstance(code, str) else None
    description_str = description if isinstance(description, str) else None
    message_str = message if isinstance(message, str) else None
    request_id_int: int | None
    if isinstance(request_id, int) and not isinstance(request_id, bool):
        request_id_int = request_id
    elif isinstance(request_id, str):
        try:
            request_id_int = int(request_id)
        except ValueError:
            request_id_int = None
    else:
        request_id_int = None
    return code_str, description_str, message_str, request_id_int


__all__ = [
    "PowensAuthError",
    "PowensBadRequestError",
    "PowensCircuitOpenError",
    "PowensConflictError",
    "PowensConnectionError",
    "PowensError",
    "PowensErrorCode",
    "PowensHTTPError",
    "PowensNotFoundError",
    "PowensRateLimitError",
    "PowensSerializationError",
    "PowensServerError",
    "PowensServiceUnavailableError",
    "parse_error_envelope",
]
