"""AccountType data model.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/bank-account-types.
"""

from __future__ import annotations

from enum import StrEnum

from powens.models.base import PowensModel


class AccountTypeName(StrEnum):
    """Documented technical codes for :attr:`AccountType.name`.

    Powens marks this enum as open; the SDK exposes the field as a
    plain ``str`` on :class:`AccountType` and this enum lists the
    documented codes for callers who want to branch on known values.
    """

    ARTICLE83 = "article83"
    CAPITALISATION = "capitalisation"
    CARD = "card"
    CAT = "cat"
    CEL = "cel"
    CHECKING = "checking"
    CROWDLENDING = "crowdlending"
    CSL = "csl"
    DEPOSIT = "deposit"
    JOINT = "joint"  # (Deprecated)
    LDDS = "ldds"
    LIFEINSURANCE = "lifeinsurance"
    LIVRET_A = "livret_a"
    LIVRET_B = "livret_b"
    LOAN = "loan"
    MADELIN = "madelin"
    MARKET = "market"
    PEA = "pea"
    PEE = "pee"
    PER = "per"
    PERCO = "perco"
    PERP = "perp"
    PEL = "pel"
    REAL_ESTATE = "real_estate"
    RSP = "rsp"
    SAVINGS = "savings"
    UNKNOWN = "unknown"


class AccountType(PowensModel):
    """A bank account type."""

    id: int
    name: str
    id_parent: int | None = None
    is_invest: bool
    display_name: str
    display_name_p: str


class AccountTypesList(PowensModel):
    """Envelope for ``GET /account_types``."""

    accounttypes: list[AccountType]


__all__ = ["AccountType", "AccountTypeName", "AccountTypesList"]
