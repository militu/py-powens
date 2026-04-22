"""Tests for the exception hierarchy and error envelope parsing."""

from __future__ import annotations

from powens.exceptions import (
    PowensAuthError,
    PowensBadRequestError,
    PowensCircuitOpenError,
    PowensConflictError,
    PowensConnectionError,
    PowensError,
    PowensErrorCode,
    PowensHTTPError,
    PowensNotFoundError,
    PowensRateLimitError,
    PowensSerializationError,
    PowensServerError,
    PowensServiceUnavailableError,
    parse_error_envelope,
)


def test_hierarchy_roots_at_powens_error() -> None:
    for cls in (
        PowensHTTPError,
        PowensBadRequestError,
        PowensAuthError,
        PowensNotFoundError,
        PowensConflictError,
        PowensRateLimitError,
        PowensServerError,
        PowensServiceUnavailableError,
        PowensConnectionError,
        PowensSerializationError,
        PowensCircuitOpenError,
    ):
        assert issubclass(cls, PowensError)


def test_http_error_exposes_parsed_envelope() -> None:
    err = PowensBadRequestError(
        "oops",
        status_code=400,
        response_body={
            "code": "invalidValue",
            "description": "Parameter 'limit' is too high",
            "message": None,
            "request_id": 123456,
        },
        request_method="GET",
        request_url="https://x/y",
        error_code="invalidValue",
        error_description="Parameter 'limit' is too high",
        error_message=None,
        request_id=123456,
    )
    assert err.status_code == 400
    assert err.error_code == "invalidValue"
    assert err.error_description == "Parameter 'limit' is too high"
    assert err.error_message is None
    assert err.request_id == 123456


def test_rate_limit_exposes_retry_after() -> None:
    err = PowensRateLimitError("slow down", retry_after=12.5)
    assert err.retry_after == 12.5
    assert err.status_code == 429


def test_error_code_enum_covers_documented_values() -> None:
    # Documented common error codes
    assert PowensErrorCode.CONNECTION_LOCKED.value == "connectionLocked"
    assert PowensErrorCode.MISSING_PARAMETER.value == "missingParameter"
    assert PowensErrorCode.INVALID_VALUE.value == "invalidValue"
    assert PowensErrorCode.METHOD_NOT_ALLOWED.value == "methodNotAllowed"
    assert PowensErrorCode.BUG.value == "bug"
    # Additional codes referenced in endpoint docs
    assert PowensErrorCode.WRONG_PASS.value == "wrongPass"
    assert PowensErrorCode.NO_ACCOUNT.value == "noAccount"


def test_parse_error_envelope_dict() -> None:
    code, desc, msg, rid = parse_error_envelope(
        {
            "code": "missingParameter",
            "description": "Missing required parameter 'client_id'",
            "message": "Please contact support",
            "request_id": 42,
        }
    )
    assert code == "missingParameter"
    assert desc == "Missing required parameter 'client_id'"
    assert msg == "Please contact support"
    assert rid == 42


def test_parse_error_envelope_handles_string_request_id() -> None:
    _, _, _, rid = parse_error_envelope({"code": "bug", "request_id": "7"})
    assert rid == 7


def test_parse_error_envelope_handles_missing_fields() -> None:
    code, desc, msg, rid = parse_error_envelope({"code": "bug"})
    assert code == "bug"
    assert desc is None
    assert msg is None
    assert rid is None


def test_parse_error_envelope_handles_non_dict() -> None:
    assert parse_error_envelope(None) == (None, None, None, None)
    assert parse_error_envelope("html error page") == (None, None, None, None)
    assert parse_error_envelope([1, 2]) == (None, None, None, None)
