"""Tests for the Lot 11 resources (Balances, AccountOwnerships, Indicators)."""

from __future__ import annotations

from datetime import date

import httpx
import respx

from powens import PowensClient
from powens.models.account_ownership import AccountPartyRole


@respx.mock
async def test_balances_get_with_date_range(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/accounts/1/balances").mock(
        return_value=httpx.Response(
            200,
            json={
                "balances": [
                    {
                        "min_date": "2024-01-01",
                        "max_date": "2024-01-31",
                        "currencies": [
                            {
                                "id": "EUR",
                                "symbol": "€",
                                "balance": "1500",
                                "expenses": "500",
                                "incomes": "2000",
                                "remains": "1500",
                            }
                        ],
                        "n_overdraft": 0,
                        "balance": "1500",
                        "expenses": "500",
                        "incomes": "2000",
                        "remains": "1500",
                        "daily_balances": [
                            {
                                "date": "2024-01-01",
                                "balance": "1000",
                                "expenses": "0",
                                "incomes": "0",
                                "remains": "0",
                            }
                        ],
                    }
                ],
                "first_date": "2024-01-01",
                "last_date": "2024-01-31",
                "result_min_date": "2024-01-01",
                "result_max_date": "2024-01-31",
            },
        )
    )
    res = await client.balances.get(
        account_id=1,
        min_date=date(2024, 1, 1),
        max_date=date(2024, 1, 31),
    )
    assert len(res.balances) == 1
    assert res.balances[0].n_overdraft == 0
    assert res.balances[0].daily_balances[0].date == date(2024, 1, 1)
    url = str(route.calls.last.request.url)
    assert "min_date=2024-01-01" in url


@respx.mock
async def test_account_ownerships_list(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/account_ownerships").mock(
        return_value=httpx.Response(
            200,
            json={
                "account_ownerships": [
                    {
                        "id_account": 1,
                        "id_connection": 2,
                        "id_user": 3,
                        "id_connector_source": 4,
                        "name": "Compte joint",
                        "bank_name": "BoursoBank",
                        "multiple_holders": True,
                        "calculated": ["multiple_holders"],
                        "usage": "PRIV",
                        "parties": [
                            {
                                "role": "co_holder",
                                "identity": {
                                    "is_user": True,
                                    "full_name": "Jane Doe",
                                },
                            }
                        ],
                        "identifications": [{"scheme_name": "iban", "identification": "FR76..."}],
                    }
                ]
            },
        )
    )
    res = await client.account_ownerships.list()
    assert res.account_ownerships[0].parties[0].role == AccountPartyRole.CO_HOLDER.value


def _mindicators() -> dict[str, object]:
    amount = {"num_statements": "10", "total_amount": 1000, "details": None}
    gambling = {
        "gambling_ratio": None,
        "income_num_statements": "0",
        "income_total_amount": 0,
        "outcome_num_statements": "0",
        "outcome_total_amount": 0,
    }
    loans = {
        "income_num_statements": "0",
        "income_total_amount": 0,
        "outcome_num_statements": "0",
        "outcome_total_amount": 0,
        "details": None,
    }
    rd = {"num_statements": "0", "total_amount": 0}
    return {
        "incoming": 3000,
        "outgoing": 2000,
        "net_cash_flow": 1000,
        "leverage_ratio": None,
        "recurrent_income": amount,
        "recurrent_outcome": amount,
        "gambling": gambling,
        "loans": loans,
        "return_debit": rd,
    }


@respx.mock
async def test_indicators_get(client: PowensClient, base_url: str) -> None:
    m = _mindicators()
    respx.get(f"{base_url}/users/me/indicators").mock(
        return_value=httpx.Response(
            200,
            json={
                "id_user": 1,
                "indicators": {
                    "avg_current_month": m,
                    "total_current_month": m,
                    "avg_last_30days": m,
                    "total_last_30days": m,
                    "avg_last_60days": m,
                    "total_last_60days": m,
                    "avg_last_90days": m,
                    "total_last_90days": m,
                },
            },
        )
    )
    res = await client.indicators.get()
    assert res.id_user == 1
    assert res.indicators is not None
    assert res.indicators.avg_current_month.incoming == 3000
