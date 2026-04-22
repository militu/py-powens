"""Investment data model and related types.

Mirrors https://docs.powens.com/api-reference/products/wealth-aggregation/investments.
"""

from __future__ import annotations

from datetime import date as _date
from datetime import datetime as _datetime
from decimal import Decimal

from pydantic import Field

from powens.models.base import PowensModel
from powens.models.currency import Currency


class InvestmentDetails(PowensModel):
    """Additional information for an investment (when enabled)."""

    performance_1_year: Decimal | None = None
    performance_3_years: Decimal | None = None
    performance_5_years: Decimal | None = None
    srri: Decimal | None = None
    asset_category: str | None = None
    recommended_period: str | None = None
    last_update: _datetime | None = None


class Investment(PowensModel):
    """An investment line held on a brokerage-like account.

    The public reference marks several fields as required
    (``code_type``, ``quantity``, ``unitprice``, ``unitvalue``,
    ``valuation``, ``diff``, ``diff_percent``, ``vdate``,
    ``portfolio_share``, ``last_update``, ``source``), but live
    payloads occasionally return them as ``null`` (e.g. for
    investments that are still being imported). The SDK therefore
    types them as optional to avoid spurious serialization failures.

    Additionally, the SDK exposes a few fields observed on live
    payloads but absent from the reference: ``id_security``,
    ``id_type``, ``stock_market``. These may disappear without notice.
    """

    id: int
    id_account: int
    label: str
    code: str | None = None
    code_type: str | None = None
    stock_symbol: str | None = None
    source: str | None = None
    description: str | None = None
    quantity: Decimal | None = None
    unitprice: Decimal | None = None
    unitvalue: Decimal | None = None
    valuation: Decimal | None = None
    diff: Decimal | None = None
    diff_percent: Decimal | None = None
    prev_diff: Decimal | None = None
    prev_diff_percent: Decimal | None = None
    vdate: _date | None = None
    prev_vdate: _date | None = None
    portfolio_share: Decimal | None = None
    calculated: list[str] = Field(default_factory=list)
    deleted: _date | None = None
    last_update: _datetime | None = None
    original_currency: Currency | None = None
    original_valuation: Decimal | None = None
    original_unitvalue: Decimal | None = None
    original_unitprice: Decimal | None = None
    original_diff: Decimal | None = None
    details: InvestmentDetails | None = None
    # Observed on live payloads but not in the public reference.
    id_security: int | None = None
    id_type: int | None = None
    stock_market: str | None = None


class InvestmentsList(PowensModel):
    """Envelope for ``GET /users/{u}/investments``."""

    investments: list[Investment]
    valuation: Decimal | None = None
    diff: Decimal | None = None
    diff_percent: Decimal | None = None
    prev_diff: Decimal | None = None
    prev_diff_percent: Decimal | None = None
    calculated: list[str] = Field(default_factory=list)


class InvestmentHistoryValue(PowensModel):
    """A snapshot in the investment history."""

    id: int
    id_investment: int
    vdate: _date
    unitvalue: Decimal
    original_currency: Currency | None = None
    original_unitvalue: Decimal | None = None


class InvestmentHistoryValuesList(PowensModel):
    """Envelope for ``GET /investments/{investmentId}/history``."""

    investmentvalues: list[InvestmentHistoryValue]


# ``InvestmentValue`` kept as a back-compat alias.
InvestmentValue = InvestmentHistoryValue


__all__ = [
    "Investment",
    "InvestmentDetails",
    "InvestmentHistoryValue",
    "InvestmentHistoryValuesList",
    "InvestmentValue",
    "InvestmentsList",
]
