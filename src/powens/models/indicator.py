"""User indicators data model.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/indicators.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from powens.models.base import PowensModel


class IndicatorMonetaryAmount(PowensModel):
    """Monetary amount used by indicator sub-objects.

    Named ``IndicatorMonetaryAmount`` to avoid collision with
    :class:`powens.models.loan_amortization.MonetaryAmount` which has a
    different shape (``currency`` + ``value`` vs. ``num_statements`` +
    ``total_amount`` + ``details``).
    """

    num_statements: Decimal
    total_amount: int
    details: str | None = None


class GamblingIndicators(PowensModel):
    """Gambling-related monthly indicators."""

    gambling_ratio: str | None = None
    income_num_statements: Decimal
    income_total_amount: int
    outcome_num_statements: Decimal
    outcome_total_amount: int


class DetailsIndicators(PowensModel):
    """One entry of :attr:`LoansIndicators.details`."""

    category_id: int
    amount: int
    date: str


class LoansIndicators(PowensModel):
    """Loan-related monthly indicators."""

    income_num_statements: Decimal
    income_total_amount: int
    outcome_num_statements: Decimal
    outcome_total_amount: int
    details: list[DetailsIndicators] | None = None


class ReturnDebitIndicators(PowensModel):
    """Return-debit monthly indicators."""

    num_statements: Decimal
    total_amount: int


class MonthlyIndicators(PowensModel):
    """A bundle of indicators for a given monthly window."""

    incoming: int
    outgoing: int
    net_cash_flow: int
    leverage_ratio: str | None = None
    recurrent_income: IndicatorMonetaryAmount
    recurrent_outcome: IndicatorMonetaryAmount
    gambling: GamblingIndicators
    loans: LoansIndicators
    return_debit: ReturnDebitIndicators


class Indicators(PowensModel):
    """User-level indicators grouped by window."""

    avg_current_month: MonthlyIndicators = Field(...)
    total_current_month: MonthlyIndicators
    avg_last_30days: MonthlyIndicators
    total_last_30days: MonthlyIndicators
    avg_last_60days: MonthlyIndicators
    total_last_60days: MonthlyIndicators
    avg_last_90days: MonthlyIndicators
    total_last_90days: MonthlyIndicators


class UserIndicators(PowensModel):
    """Envelope for ``GET /users/{u}/indicators``.

    The reference types ``indicators`` as required, but live payloads
    return ``null`` when the user has insufficient history to compute
    metrics. The SDK accepts ``None``.
    """

    id_user: int
    indicators: Indicators | None = None


__all__ = [
    "DetailsIndicators",
    "GamblingIndicators",
    "IndicatorMonetaryAmount",
    "Indicators",
    "LoansIndicators",
    "MonthlyIndicators",
    "ReturnDebitIndicators",
    "UserIndicators",
]
