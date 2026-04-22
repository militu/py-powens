"""Additional tests for the Accounts resource (Lot 8)."""

from __future__ import annotations

import httpx
import respx

from powens import PowensClient
from tests.conftest import bank_account_payload


@respx.mock
async def test_list_all_exposes_balances_map(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts").mock(
        return_value=httpx.Response(
            200,
            json={
                "accounts": [bank_account_payload(id=1, balance="100.00")],
                "balances": {"EUR": "100.00", "USD": "50.50"},
                "coming_balances": {"EUR": "10.00"},
            },
        ),
    )
    res = await client.accounts.list_all()
    assert res.balances is not None
    assert str(res.balances["EUR"]) == "100.00"
    assert res.coming_balances is not None
    assert str(res.coming_balances["EUR"]) == "10.00"


@respx.mock
async def test_account_with_loan(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts/8").mock(
        return_value=httpx.Response(
            200,
            json=bank_account_payload(
                id=8,
                type="loan",
                id_type=9,
                loan={
                    "total_amount": "200000",
                    "rate": "0.015",
                    "nb_payments_total": 240,
                    "type": "mortgage",
                },
            ),
        )
    )
    acc = await client.accounts.get(account_id=8)
    assert acc.loan is not None
    assert acc.loan.type == "mortgage"
    assert acc.loan.nb_payments_total == 240


@respx.mock
async def test_update_account_enabling_requires_all_flag(
    client: PowensClient, base_url: str
) -> None:
    route = respx.post(f"{base_url}/users/me/accounts/42").mock(
        return_value=httpx.Response(200, json=bank_account_payload(id=42)),
    )
    await client.accounts.update(
        account_id=42,
        disabled=False,
        include_all=True,
    )
    url = str(route.calls.last.request.url)
    assert "all" in url


@respx.mock
async def test_list_for_connection_uses_nested_path(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/connections/3/accounts").mock(
        return_value=httpx.Response(200, json={"accounts": []}),
    )
    async for _ in client.accounts.list(connection_id=3).by_page():
        break
    assert route.called
