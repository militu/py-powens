"""Internal async HTTP client for the Powens API.

Responsibilities:
- build the authenticated request
- send it through ``httpx``
- translate HTTP failures into the SDK's typed exceptions
- apply the retry policy (only on transient failures)
- consult / update the injected circuit breaker
- hand back parsed JSON

This layer deliberately knows nothing about Powens resources or models; those
live in :mod:`powens.resources` and :mod:`powens.models`.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from types import TracebackType
from typing import Any, Self

import httpx

from powens._http.circuit import CircuitBreaker, NoOpCircuitBreaker
from powens._http.retry import IDEMPOTENT_METHODS, RETRYABLE_STATUS_CODES, RetryPolicy
from powens.exceptions import (
    PowensAuthError,
    PowensBadRequestError,
    PowensCircuitOpenError,
    PowensConflictError,
    PowensConnectionError,
    PowensHTTPError,
    PowensNotFoundError,
    PowensRateLimitError,
    PowensServerError,
    PowensServiceUnavailableError,
    parse_error_envelope,
)

DEFAULT_TIMEOUT_SECONDS = 30.0


class HTTPClient:
    """Thin async HTTP client wrapping :class:`httpx.AsyncClient`.

    The SDK's public :class:`powens.client.PowensClient` composes this class
    rather than inheriting it.
    """

    def __init__(
        self,
        *,
        base_url: str,
        access_token: str | None = None,
        user_agent: str = "py-powens",
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_client = http_client is None
        self._base_url = base_url.rstrip("/")
        self._access_token = access_token
        self._retry_policy = retry_policy or RetryPolicy()
        self._breaker: CircuitBreaker = circuit_breaker or NoOpCircuitBreaker()

        if http_client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=timeout,
                headers={"User-Agent": user_agent, "Accept": "application/json"},
                transport=transport,
            )
        else:
            self._client = http_client

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    @property
    def access_token(self) -> str | None:
        return self._access_token

    def set_access_token(self, token: str | None) -> None:
        """Update the bearer token used on subsequent requests."""
        self._access_token = token

    async def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        data: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        auth_required: bool = True,
    ) -> Any:
        """Send a request and return the parsed JSON body.

        Empty responses (``204``) return ``None``.
        """
        response = await self.request(
            method,
            path,
            params=params,
            json_body=json_body,
            data=data,
            headers=headers,
            auth_required=auth_required,
        )
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise PowensHTTPError(
                f"Powens returned non-JSON body (status {response.status_code})",
                status_code=response.status_code,
                response_body=response.text,
                request_method=method,
                request_url=str(response.request.url),
            ) from exc

    async def get_absolute_url(self, url: str) -> Any:
        """Follow an absolute URL (e.g. a ``_links.next.href`` cursor).

        The URL must be served by the same base URL the client was built
        with; otherwise a :class:`ValueError` is raised to prevent
        exfiltrating the bearer token to an unrelated host.
        """
        if not url.startswith(self._base_url + "/") and url != self._base_url:
            raise ValueError(
                f"Refusing to follow cursor URL outside of base_url {self._base_url!r}: {url!r}"
            )
        # httpx accepts absolute URLs on request(); it will override base_url.
        return await self.request_json("GET", url)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        data: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        auth_required: bool = True,
    ) -> httpx.Response:
        """Send a request and return the raw ``httpx.Response``.

        Retries transient failures according to the configured policy. Raises
        the relevant :class:`PowensError` subclass on non-retryable or
        exhausted-retry failures.
        """
        method_upper = method.upper()
        retryable_method = (
            method_upper in IDEMPOTENT_METHODS or self._retry_policy.retry_non_idempotent
        )

        merged_headers: dict[str, str] = {}
        if auth_required and self._access_token is not None:
            merged_headers["Authorization"] = f"Bearer {self._access_token}"
        if headers:
            merged_headers.update(headers)

        cleaned_params = _drop_none_values(params)

        attempt = 0
        while True:
            attempt += 1
            if not self._breaker.allow_request():
                raise PowensCircuitOpenError("Circuit breaker is open; request short-circuited")

            try:
                response = await self._client.request(
                    method_upper,
                    path,
                    params=cleaned_params,
                    json=json_body,
                    data=data,
                    headers=merged_headers,
                )
            except httpx.TransportError as exc:
                self._breaker.record_failure()
                if retryable_method and attempt < self._retry_policy.max_attempts:
                    await asyncio.sleep(self._retry_policy.compute_delay(attempt))
                    continue
                raise PowensConnectionError(f"Network error contacting Powens: {exc}") from exc

            if response.is_success:
                self._breaker.record_success()
                return response

            if (
                retryable_method
                and response.status_code in RETRYABLE_STATUS_CODES
                and attempt < self._retry_policy.max_attempts
            ):
                self._breaker.record_failure()
                retry_after = _parse_retry_after(response.headers.get("Retry-After"))
                await asyncio.sleep(self._retry_policy.compute_delay(attempt, retry_after))
                continue

            if response.status_code >= 500:
                self._breaker.record_failure()
            raise _build_http_error(response, method=method_upper)


def _drop_none_values(params: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _build_http_error(response: httpx.Response, *, method: str) -> PowensHTTPError:
    body: Any
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = response.text

    status = response.status_code
    url = str(response.request.url)
    code, description, err_msg, request_id = parse_error_envelope(body)

    base_kwargs: dict[str, Any] = {
        "status_code": status,
        "response_body": body,
        "request_method": method,
        "request_url": url,
        "error_code": code,
        "error_description": description,
        "error_message": err_msg,
        "request_id": request_id,
    }
    suffix = f" (code={code})" if code else ""
    message = f"Powens API returned {status} for {method} {response.request.url.path}{suffix}"

    if status == 400:
        return PowensBadRequestError(message, **base_kwargs)
    if status in (401, 403):
        return PowensAuthError(message, **base_kwargs)
    if status == 404:
        return PowensNotFoundError(message, **base_kwargs)
    if status == 409:
        return PowensConflictError(message, **base_kwargs)
    if status == 429:
        return PowensRateLimitError(
            message,
            retry_after=_parse_retry_after(response.headers.get("Retry-After")),
            **base_kwargs,
        )
    if status == 503:
        return PowensServiceUnavailableError(message, **base_kwargs)
    if 500 <= status < 600:
        return PowensServerError(message, **base_kwargs)
    return PowensHTTPError(message, **base_kwargs)


__all__ = ["DEFAULT_TIMEOUT_SECONDS", "HTTPClient"]
