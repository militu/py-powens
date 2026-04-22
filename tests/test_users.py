"""Tests for the Users resource."""

from __future__ import annotations

import httpx
import respx

from powens import PowensClient


@respx.mock
async def test_me(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me").mock(
        return_value=httpx.Response(200, json={"id": 1, "signin": "2024-01-01 12:34:56"}),
    )
    user = await client.users.me()
    assert user.id == 1
    assert user.signin is not None


@respx.mock
async def test_get_by_id(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/42").mock(
        return_value=httpx.Response(200, json={"id": 42, "signin": None}),
    )
    user = await client.users.get(user_id=42)
    assert user.id == 42
    assert user.signin is None


@respx.mock
async def test_list_all(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users").mock(
        return_value=httpx.Response(
            200,
            json={"users": [{"id": 1, "signin": None}, {"id": 2, "signin": None}]},
        ),
    )
    users = await client.users.list_all()
    assert [u.id for u in users.users] == [1, 2]


@respx.mock
async def test_delete(client: PowensClient, base_url: str) -> None:
    route = respx.delete(f"{base_url}/users/99").mock(
        return_value=httpx.Response(204),
    )
    await client.users.delete(user_id=99)
    assert route.called
