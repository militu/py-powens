"""Tests for the CRUD-like resources: connections, accounts, investments."""

from __future__ import annotations

import httpx
import respx

from powens import ConnectionState, PowensClient
from tests.conftest import bank_account_payload


@respx.mock
async def test_connections_get_parses_model(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/connections/5").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 5,
                "id_user": 1,
                "id_connector": 378,
                "connector_uuid": "abc-uuid",
                # Per the Powens docs, a null state indicates a successful sync.
                "state": None,
                "active": True,
                "unknown_field": "should be ignored",
            },
        )
    )
    conn = await client.connections.get(connection_id=5)
    assert conn.id == 5
    assert conn.state is None
    assert conn.active is True
    assert conn.connector_uuid == "abc-uuid"
    # Enum still exposes the documented error states.
    assert ConnectionState.SCA_REQUIRED.value == "SCARequired"


@respx.mock
async def test_connections_force_sync_uses_put(client: PowensClient, base_url: str) -> None:
    route = respx.put(f"{base_url}/users/me/connections/5").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 5,
                "id_connector": 1,
                "connector_uuid": "u",
                "active": True,
                "state": None,
            },
        ),
    )
    conn = await client.connections.force_sync(connection_id=5)
    assert route.called
    assert conn.id == 5


@respx.mock
async def test_accounts_get(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts/8").mock(
        return_value=httpx.Response(
            200,
            json=bank_account_payload(
                id=8,
                id_connection=3,
                iban="FR761234",
                balance="1234.56",
                currency={"id": "EUR", "symbol": "€", "precision": 2},
            ),
        )
    )
    acct = await client.accounts.get(account_id=8)
    assert acct.id == 8
    assert acct.id_connection == 3
    assert str(acct.balance) == "1234.56"
    assert acct.currency is not None
    assert acct.currency.id == "EUR"


@respx.mock
async def test_accounts_list_for_connection_uses_nested_path(
    client: PowensClient, base_url: str
) -> None:
    route = respx.get(f"{base_url}/users/me/connections/3/accounts").mock(
        return_value=httpx.Response(200, json={"accounts": [], "total": 0}),
    )
    async for _ in client.accounts.list(connection_id=3).by_page():
        break
    assert route.called


def _inv(id_: int, label: str) -> dict[str, object]:
    return {
        "id": id_,
        "id_account": 12,
        "label": label,
        "code_type": "ISIN",
        "source": "website",
        "quantity": "10",
        "unitprice": "100",
        "unitvalue": "110",
        "valuation": "1100",
        "diff": "100",
        "diff_percent": "0.1",
        "vdate": "2024-01-01",
        "portfolio_share": "0.5",
        "last_update": "2024-01-01 12:00:00",
    }


@respx.mock
async def test_investments_list_by_account(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/accounts/12/investments").mock(
        return_value=httpx.Response(
            200,
            json={"investments": [_inv(1, "AAPL"), _inv(2, "MSFT")]},
        )
    )
    collected = [i async for i in client.investments.list(account_id=12)]
    assert route.called
    assert [i.id for i in collected] == [1, 2]
