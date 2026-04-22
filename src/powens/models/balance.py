"""Balances data model.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/balances.
"""

from __future__ import annotations

from datetime import date as _date
from decimal import Decimal

from pydantic import Field

from powens.models.base import PowensModel


class DailyBalance(PowensModel):
    """One entry in the ``daily_balances`` array."""

    date: _date
    balance: Decimal
    expenses: Decimal
    incomes: Decimal
    remains: Decimal


class BalanceCurrencyGroup(PowensModel):
    """Per-currency breakdown inside a :class:`BalanceGroup`."""

    id: str
    symbol: str
    balance: Decimal
    expenses: Decimal
    incomes: Decimal
    remains: Decimal


class BalanceGroup(PowensModel):
    """A grouped balance snapshot for a given period."""

    min_date: _date
    max_date: _date
    currencies: list[BalanceCurrencyGroup]
    n_overdraft: int
    balance: Decimal
    expenses: Decimal
    incomes: Decimal
    remains: Decimal
    daily_balances: list[DailyBalance] = Field(default_factory=list)


class BalanceGroupsList(PowensModel):
    """Envelope for ``GET /users/{u}/accounts/{id}/balances``."""

    balances: list[BalanceGroup]
    first_date: _date | None = None
    last_date: _date | None = None
    result_min_date: _date | None = None
    result_max_date: _date | None = None


__all__ = [
    "BalanceCurrencyGroup",
    "BalanceGroup",
    "BalanceGroupsList",
    "DailyBalance",
]
