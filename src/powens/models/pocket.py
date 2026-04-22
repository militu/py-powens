"""Pocket data model.

Mirrors https://docs.powens.com/api-reference/products/wealth-aggregation/pockets.
"""

from __future__ import annotations

from datetime import date as _date
from datetime import datetime as _datetime
from decimal import Decimal
from enum import StrEnum

from powens.models.base import PowensModel


class PocketCondition(StrEnum):
    """Documented values for :attr:`Pocket.condition`."""

    UNKNOWN = "unknown"
    DATE = "date"
    ACQUIRED = "acquired"
    AVAILABLE = "available"
    RETIREMENT = "retirement"


class Pocket(PowensModel):
    """A pocket attached to an investment (employee savings)."""

    id: int
    id_investment: int
    id_account: int
    label: str
    quantity: Decimal
    value: Decimal
    condition: str
    availability_date: _date | None = None
    deleted: _date | None = None
    last_update: _datetime


class PocketsList(PowensModel):
    """Envelope for ``GET /users/{u}/pockets``."""

    pockets: list[Pocket]


__all__ = ["Pocket", "PocketCondition", "PocketsList"]
