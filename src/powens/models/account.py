"""Bank account data model and related types.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/bank-accounts.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from powens.models.base import PowensModel
from powens.models.currency import Currency


class BankAccountUsage(StrEnum):
    """Documented values for :attr:`BankAccount.usage`."""

    PRIV = "PRIV"
    ORGA = "ORGA"


class BankAccountOwnership(StrEnum):
    """Documented values for the deprecated ``ownership`` field."""

    OWNER = "owner"
    CO_OWNER = "co-owner"
    ATTORNEY = "attorney"


class Loan(PowensModel):
    """Loan details attached to loan-type accounts."""

    total_amount: Decimal | None = None
    available_amount: Decimal | None = None
    used_amount: Decimal | None = None
    subscription_date: date | None = None
    maturity_date: date | None = None
    start_repayment_date: date | None = None
    deferred: bool | None = None
    next_payment_amount: Decimal | None = None
    next_payment_date: date | None = None
    rate: Decimal | None = None
    nb_payments_left: int | None = None
    nb_payments_done: int | None = None
    nb_payments_total: int | None = None
    last_payment_amount: Decimal | None = None
    last_payment_date: date | None = None
    account_label: str | None = None
    insurance_label: str | None = None
    insurance_amount: Decimal | None = None
    insurance_rate: Decimal | None = None
    duration: int | None = None
    type: str | None = None


class BankAccount(PowensModel):
    """A Powens bank account.

    The model mirrors the documented schema with two real-world
    adjustments over the reference:

    - ``type`` is typed as ``str`` (the Powens doc claims an
      ``AccountType`` object, but live payloads return the string code
      — which matches the field's own description).
    - Additional fields returned by live payloads but not listed in the
      reference are included (``bic``, ``coming_balance``,
      ``formatted_balance``, ``information``, ``opening_date``,
      ``webid``). These may disappear without notice since they are not
      contractually documented.
    """

    id: int
    id_connection: int | None = None
    id_user: int | None = None
    id_source: int | None = None
    id_parent: int | None = None
    number: str | None = None
    original_name: str
    balance: Decimal | None = None
    coming: Decimal | None = None
    display: bool
    last_update: datetime | None = None
    deleted: datetime | None = None
    disabled: datetime | None = None
    iban: str | None = None
    currency: Currency | None = None
    type: str
    id_type: int
    bookmarked: int
    name: str
    error: str | None = None
    usage: str | None = None
    ownership: str | None = None
    company_name: str | None = None
    loan: Loan | None = None
    # Observed on live payloads but not in the public reference.
    bic: str | None = None
    coming_balance: Decimal | None = None
    formatted_balance: str | None = None
    information: dict[str, object] | None = None
    opening_date: date | None = None
    webid: str | None = None


class Balance(PowensModel):
    """Legacy alias kept for call-site compatibility.

    The Powens documentation defines ``balances`` / ``coming_balances``
    at the list envelope level as a ``{currency: decimal}`` map; no
    standalone "Balance" model exists. This class remains so downstream
    code importing :class:`powens.models.Balance` keeps compiling.
    """

    value: Decimal | None = None
    currency: str | None = None
    date: datetime | None = None
    type: str | None = None


class BankAccountsList(PowensModel):
    """Envelope for ``GET /users/{u}/accounts``.

    ``balances`` and ``coming_balances`` are associative maps keyed by
    ISO currency code. We store them as ``dict[str, Decimal]``.

    The top-level ``balance`` / ``total`` fields appear on live
    envelopes but are not documented — we accept them so the raw
    payload round-trips cleanly.
    """

    accounts: list[BankAccount]
    balances: dict[str, Decimal] | None = None
    coming_balances: dict[str, Decimal] | None = None
    # Observed on live payloads but not in the public reference.
    balance: Decimal | None = None
    total: int | None = None


class BankAccountUpdateRequest(PowensModel):
    """Request body for ``POST /users/{u}/accounts/{id}``."""

    display: bool | None = None
    name: str | None = None
    disabled: bool | None = None
    bookmarked: bool | None = None
    usage: str | None = None


# ``Account`` is kept as a thin re-export of :class:`BankAccount` for
# backwards-compatibility; previous SDK releases used this name.
Account = BankAccount


__all__ = [
    "Account",
    "Balance",
    "BankAccount",
    "BankAccountOwnership",
    "BankAccountUpdateRequest",
    "BankAccountUsage",
    "BankAccountsList",
    "Loan",
]
