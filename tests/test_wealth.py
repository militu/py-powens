"""Tests for the Lot 10 resources (Investments, MarketOrders, Pockets, Amortizations)."""

from __future__ import annotations

import httpx
import respx

from powens import PowensClient
from powens.models.pocket import PocketCondition


def _inv(id_: int = 1) -> dict[str, object]:
    return {
        "id": id_,
        "id_account": 10,
        "label": "ETF World",
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
async def test_investments_list_all_exposes_aggregates(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/investments").mock(
        return_value=httpx.Response(
            200,
            json={
                "valuation": "2200",
                "diff": "200",
                "diff_percent": "0.1",
                "prev_diff": "100",
                "prev_diff_percent": "0.05",
                "calculated": ["diff"],
                "investments": [_inv(1), _inv(2)],
            },
        )
    )
    env = await client.investments.list_all()
    assert str(env.valuation) == "2200"
    assert env.calculated == ["diff"]


@respx.mock
async def test_investment_history(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/investments/7/history").mock(
        return_value=httpx.Response(
            200,
            json={
                "investmentvalues": [
                    {
                        "id": 1,
                        "id_investment": 7,
                        "vdate": "2024-01-01",
                        "unitvalue": "100.00",
                    },
                    {
                        "id": 2,
                        "id_investment": 7,
                        "vdate": "2024-01-02",
                        "unitvalue": "101.50",
                    },
                ]
            },
        )
    )
    hist = await client.investments.history(investment_id=7)
    assert len(hist.investmentvalues) == 2


@respx.mock
async def test_market_orders_list(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/marketorders").mock(
        return_value=httpx.Response(
            200,
            json={
                "marketorders": [
                    {
                        "id": 1,
                        "id_account": 10,
                        "number": "MO-001",
                        "label": "Buy AAPL",
                        "code": "US0378331005",
                        "stock_symbol": "AAPL",
                        "order_direction": {"id": 1, "name": "BUY"},
                        "order_type": {"id": 1, "name": "MARKET"},
                        "state": "Executed",
                        "payment_method": "CASH",
                        "quantity": "10",
                        "amount": "1500",
                        "last_update": "2024-01-01 10:00:00",
                    }
                ]
            },
        )
    )
    res = await client.market_orders.list()
    assert res.marketorders[0].order_direction.name == "BUY"


@respx.mock
async def test_pockets_list_by_investment(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/investments/5/pockets").mock(
        return_value=httpx.Response(
            200,
            json={
                "pockets": [
                    {
                        "id": 1,
                        "id_investment": 5,
                        "id_account": 10,
                        "label": "Vested tranche 2023",
                        "quantity": "100",
                        "value": "1100",
                        "condition": "available",
                        "availability_date": "2024-01-01",
                        "last_update": "2024-01-01 12:00:00",
                    }
                ]
            },
        )
    )
    res = await client.pockets.list(investment_id=5)
    assert res.pockets[0].condition == PocketCondition.AVAILABLE.value


@respx.mock
async def test_loan_amortizations_list(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users/me/amortizations").mock(
        return_value=httpx.Response(
            200,
            json={
                "loanamortizations": [
                    {
                        "id_account": 10,
                        "payment_date": "2024-01-15",
                        "amortization_amount": {"currency": "EUR", "value": "500"},
                        "interest_amount": {"currency": "EUR", "value": "50"},
                        "insurance_amount": {"currency": "EUR", "value": "10"},
                        "total_payment_amount": {"currency": "EUR", "value": "560"},
                        "remaining_capital": {"currency": "EUR", "value": "95000"},
                        "period": "2024_01",
                        "calculated": [],
                        "last_update": "2024-01-01 12:00:00",
                    }
                ]
            },
        )
    )
    res = await client.loan_amortizations.list()
    assert res.loanamortizations[0].period == "2024_01"
    assert str(res.loanamortizations[0].total_payment_amount.value) == "560"
