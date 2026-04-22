"""Market order data model.

Mirrors https://docs.powens.com/api-reference/products/wealth-aggregation/market-orders.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from powens.models.base import PowensModel


class MarketOrderDirection(PowensModel):
    """Market order direction (``BUY``/``SALE``)."""

    id: int
    name: str


class MarketOrderType(PowensModel):
    """Market order type (``MARKET``/``LIMIT``/``TRIGGER``/``UNKNOWN``)."""

    id: int
    name: str


class MarketOrder(PowensModel):
    """A market order held on a brokerage-like account."""

    id: int
    id_account: int
    number: str
    label: str
    code: str | None = None
    stock_symbol: str | None = None
    order_direction: MarketOrderDirection
    order_type: MarketOrderType
    stock_market: str | None = None
    state: str
    payment_method: str
    date: datetime | None = None
    execution_date: datetime | None = None
    validity_date: datetime | None = None
    quantity: Decimal | None = None
    amount: Decimal | None = None
    ordervalue: Decimal | None = None
    unitprice: Decimal | None = None
    unitvalue: Decimal | None = None
    deleted: datetime | None = None
    last_update: datetime


class MarketOrdersList(PowensModel):
    """Envelope for ``GET /users/{u}/marketorders``."""

    marketorders: list[MarketOrder]


__all__ = [
    "MarketOrder",
    "MarketOrderDirection",
    "MarketOrderType",
    "MarketOrdersList",
]
