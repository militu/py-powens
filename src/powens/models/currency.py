"""Currency data model.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/currencies.
"""

from __future__ import annotations

from datetime import datetime as _datetime
from decimal import Decimal

from powens.models.base import PowensModel


class Currency(PowensModel):
    """A supported currency.

    ``crypto`` is documented as deprecated but kept for fidelity.

    Additional fields observed on live payloads but absent from the
    public reference: ``prefix``, ``marketcap``, ``datetime``. These
    may disappear without notice.
    """

    id: str
    name: str | None = None
    symbol: str | None = None
    crypto: bool | None = None
    precision: int | None = None
    # Observed on live payloads but not in the public reference.
    prefix: bool | None = None
    marketcap: Decimal | None = None
    datetime: _datetime | None = None


class CurrenciesList(PowensModel):
    """Envelope for ``GET /currencies``."""

    currencies: list[Currency]


__all__ = ["CurrenciesList", "Currency"]
