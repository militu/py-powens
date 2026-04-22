"""Tests for the Transactions resource (Lot 9)."""

from __future__ import annotations

from datetime import date

import httpx
import respx

from powens import PowensClient
from powens.models.transaction import (
    AccountSchemeName,
    Transaction,
    TransactionType,
)


def _tx(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "id": 1,
        "id_account": 10,
        "application_date": "2024-01-02",
        "date": "2024-01-01",
        "rdate": "2024-01-01",
        "value": "-42.50",
        "type": "card",
        "original_wording": "CARD xx ORIG",
        "simplified_wording": "Groceries",
        "date_scraped": "2024-01-02 10:00:00",
        "coming": False,
        "active": True,
    }
    body.update(overrides)
    return body


def test_transaction_type_enum_documented_values() -> None:
    # loan_repayment (not loan_payment); the other 19 documented values.
    values = {
        "transfer",
        "order",
        "check",
        "deposit",
        "payback",
        "withdrawal",
        "loan_repayment",
        "bank",
        "card",
        "deferred_card",
        "summary_card",
        "unknown",
        "market_order",
        "market_fee",
        "arbitrage",
        "profit",
        "refund",
        "payout",
        "payment",
        "fee",
    }
    enum_values = {t.value for t in TransactionType}
    assert values == enum_values


def test_account_scheme_name_enum() -> None:
    assert {x.value for x in AccountSchemeName} == {
        "iban",
        "bban",
        "sort_code_account_number",
        "cpan",
        "tpan",
    }


def test_transaction_parses_full_payload() -> None:
    tx = Transaction.model_validate(
        _tx(
            datetime="2024-01-01 08:30:00",
            vdate="2024-01-01",
            vdatetime="2024-01-01 08:30:00",
            categories=[{"code": "groceries", "parent_code": "food_and_restaurants"}],
            counterparty={
                "label": "SuperMarket",
                "account_scheme_name": "iban",
                "account_identification": "FR76...",
                "type": "creditor",
            },
            original_value="-50.00",
            original_currency={"id": "USD", "precision": 2},
            commission="0.50",
            commission_currency={"id": "EUR", "precision": 2},
        )
    )
    assert tx.counterparty is not None
    assert tx.counterparty.label == "SuperMarket"
    assert tx.original_currency is not None
    assert tx.original_currency.id == "USD"
    assert len(tx.categories) == 1


@respx.mock
async def test_list_uses_cursor_pagination(client: PowensClient, base_url: str) -> None:
    """Cursor-based pagination follows ``_links.next.href`` verbatim."""
    cursor_page = httpx.Response(
        200,
        json={
            "transactions": [_tx(id=3)],
            "_links": {"self": None, "prev": None, "next": None},
        },
    )
    first_page = httpx.Response(
        200,
        json={
            "transactions": [_tx(id=1), _tx(id=2)],
            "first_date": "2024-01-01",
            "last_date": "2024-01-31",
            "result_min_date": "2024-01-01",
            "result_max_date": "2024-01-02",
            "_links": {
                "self": {"href": f"{base_url}/users/me/transactions?limit=2"},
                "prev": None,
                "next": {"href": f"{base_url}/users/me/transactions?limit=2&cursor=Wxxx"},
            },
        },
    )
    # respx matches by insertion order on duplicate paths; route the cursor
    # variant FIRST so it wins over the generic initial route.
    respx.get(
        f"{base_url}/users/me/transactions",
        params={"cursor": "Wxxx"},
    ).mock(return_value=cursor_page)
    respx.get(f"{base_url}/users/me/transactions").mock(return_value=first_page)

    collected = [tx async for tx in client.transactions.list(limit=2)]
    assert [tx.id for tx in collected] == [1, 2, 3]


@respx.mock
async def test_list_page_exposes_envelope_dates(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/accounts/7/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "transactions": [_tx(id=1)],
                "first_date": "2024-01-01",
                "last_date": "2024-01-31",
                "result_min_date": "2024-01-01",
                "result_max_date": "2024-01-02",
                "_links": {"self": None, "prev": None, "next": None},
            },
        )
    )
    envelope = await client.transactions.list_page(
        account_id=7,
        min_date=date(2024, 1, 1),
        max_date=date(2024, 1, 31),
    )
    assert envelope.first_date == date(2024, 1, 1)
    assert envelope.last_date == date(2024, 1, 31)
    assert envelope.links is not None


@respx.mock
async def test_update_transaction(client: PowensClient, base_url: str) -> None:
    route = respx.post(f"{base_url}/users/me/transactions/1").mock(
        return_value=httpx.Response(200, json=_tx(id=1, wording="Edited")),
    )
    tx = await client.transactions.update(
        transaction_id=1,
        wording="Edited",
        categories=[{"code": "groceries", "parent_code": "food_and_restaurants"}],
    )
    assert tx.wording == "Edited"
    assert route.called


@respx.mock
async def test_list_forwards_limit_and_filters(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "transactions": [],
                "_links": {"self": None, "prev": None, "next": None},
            },
        )
    )
    pages = client.transactions.list(
        limit=500,
        min_date=date(2024, 1, 1),
        max_date=date(2024, 12, 31),
        deleted=False,
        income=True,
    )
    async for _ in pages.by_page():
        break
    url = str(route.calls.last.request.url)
    assert "limit=500" in url
    assert "min_date=2024-01-01" in url
    assert "max_date=2024-12-31" in url
    assert "deleted=false" in url
    assert "income=true" in url
