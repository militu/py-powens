"""Transaction data model and related types.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/bank-transactions.
"""

from __future__ import annotations

from datetime import date as _date
from datetime import datetime as _datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from powens.models.base import PowensModel
from powens.models.currency import Currency
from powens.models.pagination import PaginationLinks


class TransactionType(StrEnum):
    """All documented transaction types."""

    TRANSFER = "transfer"
    ORDER = "order"
    CHECK = "check"
    DEPOSIT = "deposit"
    PAYBACK = "payback"
    WITHDRAWAL = "withdrawal"
    LOAN_REPAYMENT = "loan_repayment"
    BANK = "bank"
    CARD = "card"
    DEFERRED_CARD = "deferred_card"
    SUMMARY_CARD = "summary_card"
    UNKNOWN = "unknown"
    MARKET_ORDER = "market_order"
    MARKET_FEE = "market_fee"
    ARBITRAGE = "arbitrage"
    PROFIT = "profit"
    REFUND = "refund"
    PAYOUT = "payout"
    PAYMENT = "payment"
    FEE = "fee"


class AccountSchemeName(StrEnum):
    """Documented values for :attr:`Counterparty.account_scheme_name`."""

    IBAN = "iban"
    BBAN = "bban"
    SORT_CODE_ACCOUNT_NUMBER = "sort_code_account_number"
    CPAN = "cpan"
    TPAN = "tpan"


class Category(PowensModel):
    """A transaction category."""

    code: str
    parent_code: str | None = None


class Counterparty(PowensModel):
    """A transaction counterparty (creditor/debtor)."""

    label: str | None = None
    account_scheme_name: str | None = None
    account_identification: str | None = None
    type: str | None = None


class Attachment(PowensModel):
    """A transaction attachment (feature-gated)."""

    id: int
    name: str
    description: str | None = None
    mime_type: str
    size: int
    created_date: _date | None = None
    created_datetime: _datetime | None = None
    last_update: _datetime | None = None
    url: str


class Transaction(PowensModel):
    """A Powens bank transaction.

    The model mirrors the documented fields one-to-one, including the
    deprecated ``bdate``/``bdatetime``/``country`` fields which may still
    appear on live payloads.
    """

    id: int
    id_account: int
    application_date: _date | None = None
    date: _date
    datetime: _datetime | None = None
    vdate: _date | None = None
    vdatetime: _datetime | None = None
    rdate: _date
    rdatetime: _datetime | None = None
    bdate: _date | None = None  # Deprecated
    bdatetime: _datetime | None = None  # Deprecated
    value: Decimal | None = None
    gross_value: Decimal | None = None
    type: str
    original_wording: str
    simplified_wording: str
    wording: str | None = None
    categories: list[Category] = Field(default_factory=list)
    date_scraped: _datetime
    coming: bool
    active: bool
    id_cluster: int | None = None
    comment: str | None = None
    last_update: _datetime | None = None
    deleted: _datetime | None = None
    original_value: Decimal | None = None
    original_gross_value: Decimal | None = None
    original_currency: Currency | None = None
    commission: Decimal | None = None
    commission_currency: Currency | None = None
    country: str | None = None  # Deprecated
    card: str | None = None
    counterparty: Counterparty | None = None
    # Expanded when ``?expand=attachments`` is requested.
    attachments: list[Attachment] | None = None


class TransactionsList(PowensModel):
    """Envelope for ``GET /users/{u}/transactions`` (relational pagination)."""

    transactions: list[Transaction]
    first_date: _date | None = None
    last_date: _date | None = None
    result_min_date: _date | None = None
    result_max_date: _date | None = None
    links: PaginationLinks | None = Field(default=None, alias="_links")


class TransactionUpdateRequest(PowensModel):
    """Request body for ``POST /users/{u}/transactions/{transactionId}``."""

    wording: str | None = None
    application_date: _date | None = None
    categories: list[Category] | None = None
    comment: str | None = None
    active: bool | None = None


__all__ = [
    "AccountSchemeName",
    "Attachment",
    "Category",
    "Counterparty",
    "Transaction",
    "TransactionType",
    "TransactionUpdateRequest",
    "TransactionsList",
]
