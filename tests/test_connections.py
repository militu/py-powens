"""Tests for the Connections resource (create/update/sync/sources/logs/webauth)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from powens import PowensClient


def _conn(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "id": 1,
        "id_connector": 10,
        "connector_uuid": "uuid-abc",
        "active": True,
        "state": None,
    }
    body.update(overrides)
    return body


@respx.mock
async def test_create_requires_connector_identifier(client: PowensClient) -> None:
    with pytest.raises(ValueError, match="id_connector"):
        await client.connections.create()


@respx.mock
async def test_create_sends_connector_uuid_and_fields(client: PowensClient, base_url: str) -> None:
    route = respx.post(f"{base_url}/users/me/connections").mock(
        return_value=httpx.Response(201, json=_conn()),
    )
    await client.connections.create(
        connector_uuid="uuid-abc",
        fields={"login": "user@example", "password": "s3cret"},
    )
    sent = json.loads(route.calls.last.request.content)
    assert sent["connector_uuid"] == "uuid-abc"
    assert sent["login"] == "user@example"
    assert sent["password"] == "s3cret"


@respx.mock
async def test_update_submits_otp_via_fields(client: PowensClient, base_url: str) -> None:
    route = respx.post(f"{base_url}/users/me/connections/1").mock(
        return_value=httpx.Response(200, json=_conn()),
    )
    await client.connections.update(
        connection_id=1,
        fields={"otp": "123456"},
    )
    sent = json.loads(route.calls.last.request.content)
    assert sent == {"otp": "123456"}


@respx.mock
async def test_sync_uses_put_with_psu_requested_flag(client: PowensClient, base_url: str) -> None:
    route = respx.put(f"{base_url}/users/me/connections/1").mock(
        return_value=httpx.Response(200, json=_conn()),
    )
    await client.connections.sync(connection_id=1, psu_requested=False)
    url = str(route.calls.last.request.url)
    assert "psu_requested=false" in url


@respx.mock
async def test_delete_returns_none_on_204(client: PowensClient, base_url: str) -> None:
    route = respx.delete(f"{base_url}/users/me/connections/1").mock(
        return_value=httpx.Response(204),
    )
    await client.connections.delete(connection_id=1)
    assert route.called


@respx.mock
async def test_list_sources_with_all_flag(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/connections/1/sources").mock(
        return_value=httpx.Response(
            200,
            json={
                "sources": [
                    {
                        "id": 7,
                        "id_connection": 1,
                        "id_connector_source": 3,
                        "name": "direct",
                        "last_update": None,
                        "disabled": None,
                        "created": "2024-01-01 00:00:00",
                        "state": None,
                        "access_expire": None,
                        "expire": None,
                        "next_try": None,
                    }
                ]
            },
        ),
    )
    res = await client.connections.list_sources(connection_id=1, include_all=True)
    assert len(res.sources) == 1
    assert "all" in str(route.calls.last.request.url)


@respx.mock
async def test_update_source(client: PowensClient, base_url: str) -> None:
    route = respx.post(f"{base_url}/users/me/connections/1/sources/7").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 7,
                "id_connection": 1,
                "id_connector_source": 3,
                "name": "direct",
                "last_update": None,
                "disabled": None,
                "created": "2024-01-01 00:00:00",
                "state": None,
                "access_expire": None,
                "expire": None,
                "next_try": None,
            },
        ),
    )
    res = await client.connections.update_source(connection_id=1, source_id=7, disabled=True)
    assert res.id == 7
    body = json.loads(route.calls.last.request.content)
    assert body == {"disabled": True}


@respx.mock
async def test_webauth_url(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/webauth-url").mock(
        return_value=httpx.Response(200, json={"url": "https://bank/webauth?session=xyz"}),
    )
    res = await client.connections.webauth_url(
        client_id=123,
        redirect_uri="https://app/cb",
        id_connection=1,
    )
    assert res.url.startswith("https://bank/webauth?")


@respx.mock
async def test_list_all_vs_list_lazy(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/connections").mock(
        return_value=httpx.Response(
            200,
            json={"connections": [_conn(), _conn(id=2)]},
        )
    )
    bundled = await client.connections.list_all()
    assert {c.id for c in bundled.connections} == {1, 2}
