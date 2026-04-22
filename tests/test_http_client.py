"""Tests for the internal HTTP client: auth header, errors, retries, circuit."""

from __future__ import annotations

import httpx
import pytest
import respx

from powens import (
    PowensAuthError,
    PowensBadRequestError,
    PowensCircuitOpenError,
    PowensClient,
    PowensConflictError,
    PowensConnectionError,
    PowensHTTPError,
    PowensNotFoundError,
    PowensRateLimitError,
    PowensServerError,
    PowensServiceUnavailableError,
    RetryPolicy,
)
from powens._http.circuit import CircuitBreaker
from tests.conftest import bank_account_payload


@respx.mock
async def test_sends_bearer_auth_header(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/accounts").mock(
        return_value=httpx.Response(200, json={"accounts": [], "total": 0}),
    )
    pages = client.accounts.list()
    async for _ in pages.by_page():
        break
    assert route.called
    sent = route.calls.last.request
    assert sent.headers["Authorization"] == "Bearer test-token"
    assert sent.headers["User-Agent"] == "py-powens"


@respx.mock
async def test_maps_400_to_bad_request(client_no_retry: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts/7").mock(
        return_value=httpx.Response(
            400,
            json={
                "code": "invalidValue",
                "description": "bad param",
                "message": None,
                "request_id": 99,
            },
        )
    )
    with pytest.raises(PowensBadRequestError) as ei:
        await client_no_retry.accounts.get(account_id=7)
    assert ei.value.status_code == 400
    assert ei.value.error_code == "invalidValue"
    assert ei.value.error_description == "bad param"
    assert ei.value.error_message is None
    assert ei.value.request_id == 99


@respx.mock
async def test_maps_401_to_auth_error(client_no_retry: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts").mock(
        return_value=httpx.Response(
            401,
            json={"code": "invalidToken", "description": "expired", "message": None},
        ),
    )
    with pytest.raises(PowensAuthError) as ei:
        async for _ in client_no_retry.accounts.list().by_page():
            break
    assert ei.value.status_code == 401
    assert ei.value.error_code == "invalidToken"
    assert ei.value.error_description == "expired"


@respx.mock
async def test_maps_404_to_not_found(client_no_retry: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts/42").mock(return_value=httpx.Response(404))
    with pytest.raises(PowensNotFoundError):
        await client_no_retry.accounts.get(account_id=42)


@respx.mock
async def test_maps_409_to_conflict(client_no_retry: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts/7").mock(
        return_value=httpx.Response(409, json={"code": "invalidValue"}),
    )
    with pytest.raises(PowensConflictError) as ei:
        await client_no_retry.accounts.get(account_id=7)
    assert ei.value.status_code == 409
    assert ei.value.error_code == "invalidValue"


@respx.mock
async def test_maps_500_to_server_error(client_no_retry: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts/7").mock(
        return_value=httpx.Response(500, json={"code": "bug"}),
    )
    with pytest.raises(PowensServerError) as ei:
        await client_no_retry.accounts.get(account_id=7)
    assert ei.value.status_code == 500
    assert ei.value.error_code == "bug"


@respx.mock
async def test_maps_503_to_service_unavailable(
    client_no_retry: PowensClient, base_url: str
) -> None:
    respx.get(f"{base_url}/users/me/accounts/7").mock(return_value=httpx.Response(503))
    with pytest.raises(PowensServiceUnavailableError) as ei:
        await client_no_retry.accounts.get(account_id=7)
    assert ei.value.status_code == 503


@respx.mock
async def test_maps_429_to_rate_limit_and_retries_with_retry_after(
    client: PowensClient, base_url: str
) -> None:
    route = respx.get(f"{base_url}/users/me/accounts").mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0"}, json={}),
            httpx.Response(200, json={"accounts": [], "total": 0}),
        ]
    )
    async for _ in client.accounts.list().by_page():
        break
    assert route.call_count == 2


@respx.mock
async def test_exhausts_retries_then_raises_rate_limit(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/accounts").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "0"}),
    )
    with pytest.raises(PowensRateLimitError):
        async for _ in client.accounts.list().by_page():
            break
    assert route.call_count == 3  # max_attempts == 3


@respx.mock
async def test_retries_on_transient_5xx(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/accounts").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json={"accounts": []}),
        ]
    )
    async for _ in client.accounts.list().by_page():
        break
    assert route.call_count == 2


@respx.mock
async def test_does_not_retry_non_idempotent_by_default(
    client: PowensClient, base_url: str
) -> None:
    route = respx.post(f"{base_url}/auth/init").mock(return_value=httpx.Response(503))
    with pytest.raises(PowensHTTPError):
        await client.auth.init_user(client_id="cid", client_secret="csec")
    assert route.call_count == 1


@respx.mock
async def test_connection_error_maps_to_typed_exception(
    client_no_retry: PowensClient, base_url: str
) -> None:
    respx.get(f"{base_url}/users/me/accounts").mock(
        side_effect=httpx.ConnectError("boom"),
    )
    with pytest.raises(PowensConnectionError):
        async for _ in client_no_retry.accounts.list().by_page():
            break


@respx.mock
async def test_injected_circuit_breaker_short_circuits(base_url: str) -> None:
    class OpenBreaker(CircuitBreaker):
        def allow_request(self) -> bool:
            return False

        def record_success(self) -> None:
            return None

        def record_failure(self) -> None:
            return None

    async with PowensClient(
        base_url=base_url,
        access_token="t",
        circuit_breaker=OpenBreaker(),
    ) as client:
        with pytest.raises(PowensCircuitOpenError):
            await client.accounts.get(account_id=1)


@respx.mock
async def test_injected_breaker_sees_success_and_failure(
    base_url: str,
) -> None:
    calls: list[str] = []

    class TrackingBreaker(CircuitBreaker):
        def allow_request(self) -> bool:
            return True

        def record_success(self) -> None:
            calls.append("success")

        def record_failure(self) -> None:
            calls.append("failure")

    respx.get(f"{base_url}/users/me/accounts/1").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json=bank_account_payload(id=1)),
        ]
    )
    retry = RetryPolicy(max_attempts=3, base_delay=0.0, jitter=0.0)
    async with PowensClient(
        base_url=base_url,
        access_token="t",
        retry_policy=retry,
        circuit_breaker=TrackingBreaker(),
    ) as client:
        acct = await client.accounts.get(account_id=1)
    assert acct.id == 1
    assert calls == ["failure", "success"]


@respx.mock
async def test_non_json_body_raises_http_error(
    client_no_retry: PowensClient, base_url: str
) -> None:
    respx.get(f"{base_url}/users/me/accounts/7").mock(
        return_value=httpx.Response(200, content=b"<html>not json</html>"),
    )
    with pytest.raises(PowensHTTPError):
        await client_no_retry.accounts.get(account_id=7)


@respx.mock
async def test_204_returns_none(base_url: str) -> None:
    route = respx.delete(f"{base_url}/users/me/connections/9").mock(
        return_value=httpx.Response(204),
    )
    async with PowensClient(base_url=base_url, access_token="t") as client:
        await client.connections.delete(connection_id=9)
    assert route.called
