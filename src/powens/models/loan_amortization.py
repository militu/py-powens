"""Loan amortization data model.

Mirrors https://docs.powens.com/api-reference/products/wealth-aggregation/loan-amortizations.
"""

from __future__ import annotations

from datetime import date as _date
from datetime import datetime as _datetime
from decimal import Decimal

from pydantic import Field

from powens.models.base import PowensModel


class MonetaryAmount(PowensModel):
    """A currency + amount pair as documented under loan amortizations.

    The Powens reference uses the same object name in several places;
    this copy lives here because its shape matches the loan-specific
    documentation (``currency: string``, ``value: Decimal | None``).
    """

    currency: str
    value: Decimal | None = None


class LoanAmortization(PowensModel):
    """A single loan amortization entry."""

    id_account: int
    payment_date: _date | None = None
    amortization_amount: MonetaryAmount
    interest_amount: MonetaryAmount
    insurance_amount: MonetaryAmount
    total_payment_amount: MonetaryAmount
    remaining_capital: MonetaryAmount
    period: str
    calculated: list[str] = Field(default_factory=list)
    deleted: _datetime | None = None
    last_update: _datetime


class LoanAmortizationsList(PowensModel):
    """Envelope for ``GET /users/{u}/amortizations``."""

    loanamortizations: list[LoanAmortization]


__all__ = ["LoanAmortization", "LoanAmortizationsList", "MonetaryAmount"]
