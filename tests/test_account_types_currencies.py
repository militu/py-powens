"""Tests for AccountTypes and Currencies resources."""

from __future__ import annotations

import httpx
import respx

from powens import PowensClient
from powens.models.account_type import AccountTypeName


@respx.mock
async def test_list_account_types(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/account_types").mock(
        return_value=httpx.Response(
            200,
            json={
                "accounttypes": [
                    {
                        "id": 1,
                        "name": "checking",
                        "id_parent": None,
                        "is_invest": False,
                        "display_name": "Compte courant",
                        "display_name_p": "Comptes courants",
                    },
                ],
            },
        )
    )
    res = await client.account_types.list()
    assert res.accounttypes[0].name == AccountTypeName.CHECKING.value


@respx.mock
async def test_get_account_type(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/account_types/42").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 42,
                "name": "pea",
                "id_parent": None,
                "is_invest": True,
                "display_name": "PEA",
                "display_name_p": "PEAs",
            },
        )
    )
    at = await client.account_types.get(type_id=42)
    assert at.is_invest is True


@respx.mock
async def test_list_currencies(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/currencies").mock(
        return_value=httpx.Response(
            200,
            json={
                "currencies": [
                    {
                        "id": "EUR",
                        "name": "Euro",
                        "symbol": "€",
                        "crypto": False,
                        "precision": 2,
                    },
                    {"id": "USD", "name": "US Dollar", "symbol": "$", "precision": 2},
                ],
            },
        )
    )
    res = await client.currencies.list()
    assert {c.id for c in res.currencies} == {"EUR", "USD"}
