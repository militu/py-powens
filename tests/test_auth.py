"""Tests for the auth resource (user and service tokens)."""

from __future__ import annotations

import httpx
import respx

from powens import PowensClient
from powens.models.auth import AuthScope


@respx.mock
async def test_init_user_sends_credentials_without_auth_header(base_url: str) -> None:
    route = respx.post(f"{base_url}/auth/init").mock(
        return_value=httpx.Response(
            200,
            json={
                "auth_token": "tok",
                "type": "permanent",
                "id_user": 42,
                "expires_in": None,
            },
        ),
    )
    async with PowensClient(base_url=base_url) as client:
        token = await client.auth.init_user(client_id="cid", client_secret="csec")
    assert token.auth_token == "tok"
    assert token.type == "permanent"
    assert token.id_user == 42
    assert route.called
    # No bearer token configured, so no Authorization header expected.
    sent = route.calls.last.request
    assert "Authorization" not in sent.headers
    assert b'"client_id"' in sent.content


@respx.mock
async def test_generate_code_sends_type_query_param(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/auth/token/code").mock(
        return_value=httpx.Response(
            200,
            json={
                "code": "temp-123",
                "type": "temporary",
                "access": "single",
                "expires_in": 1800,
            },
        ),
    )
    code = await client.auth.generate_code(type_="singleAccess")
    assert code.code == "temp-123"
    assert code.type == "temporary"
    assert code.access == "single"
    assert code.expires_in == 1800
    assert route.called
    assert "type=singleAccess" in str(route.calls.last.request.url)


@respx.mock
async def test_exchange_code(client: PowensClient, base_url: str) -> None:
    route = respx.post(f"{base_url}/auth/token/access").mock(
        return_value=httpx.Response(200, json={"access_token": "perm-tok", "token_type": "Bearer"}),
    )
    res = await client.auth.exchange_code(code="abc", client_id="cid", client_secret="csec")
    assert res.access_token == "perm-tok"
    assert res.token_type == "Bearer"
    assert route.called
    body = route.calls.last.request.content
    assert b"authorization_code" in body


@respx.mock
async def test_revoke_token_calls_delete_auth_token(client: PowensClient, base_url: str) -> None:
    route = respx.delete(f"{base_url}/auth/token").mock(return_value=httpx.Response(204))
    await client.auth.revoke_token()
    assert route.called


@respx.mock
async def test_renew_token(client: PowensClient, base_url: str) -> None:
    respx.post(f"{base_url}/auth/renew").mock(
        return_value=httpx.Response(200, json={"access_token": "new", "token_type": "Bearer"}),
    )
    res = await client.auth.renew_token(
        client_id="cid",
        client_secret="csec",
        id_user=42,
        revoke_previous=True,
    )
    assert res.access_token == "new"


@respx.mock
async def test_generate_service_token_accepts_single_scope(
    client: PowensClient, base_url: str
) -> None:
    route = respx.post(f"{base_url}/auth/token").mock(
        return_value=httpx.Response(200, json={"token": "svc", "scope": "payments:admin"}),
    )
    res = await client.auth.generate_service_token(
        client_id="cid",
        client_secret="csec",
        scope=AuthScope.PAYMENTS_ADMIN,
    )
    assert res.token == "svc"
    assert res.scope == "payments:admin"
    assert route.called
    sent_body = route.calls.last.request.content
    assert b"payments:admin" in sent_body


@respx.mock
async def test_generate_service_token_accepts_list_scope(
    client: PowensClient, base_url: str
) -> None:
    respx.post(f"{base_url}/auth/token").mock(
        return_value=httpx.Response(200, json={"token": "svc", "scope": "payments:read-only"}),
    )
    await client.auth.generate_service_token(
        client_id="cid",
        client_secret="csec",
        scope=[AuthScope.PAYMENTS_READ_ONLY, "payment-links:admin"],
    )
