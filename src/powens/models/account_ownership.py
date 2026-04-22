"""Account ownership data model.

Mirrors
https://docs.powens.com/api-reference/products/data-aggregation/account-ownerships.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from powens.models.base import PowensModel


class AccountPartyRole(StrEnum):
    """Documented values for :attr:`AccountParty.role`."""

    HOLDER = "holder"
    CO_HOLDER = "co_holder"
    ATTORNEY = "attorney"
    CUSTODIAN_FOR_MINOR = "custodian_for_minor"
    LEGAL_GUARDIAN = "legal_guardian"
    NOMINEE = "nominee"
    SUCCESSOR_ON_DEATH = "successor_on_death"
    TRUSTEE = "trustee"
    UNKNOWN = "unknown"


class IdentityParty(PowensModel):
    """The identity portion of an :class:`AccountParty`."""

    is_user: bool | None = None
    full_name: str


class AccountParty(PowensModel):
    """An account party (holder / co-holder / …)."""

    role: str
    identity: IdentityParty


class AccountIdentification(PowensModel):
    """One entry of :attr:`AccountOwnership.identifications`."""

    scheme_name: str
    identification: str


class AccountOwnership(PowensModel):
    """The ownership breakdown of a bank account."""

    id_account: int
    id_connection: int
    id_user: int
    id_connector_source: int
    name: str | None = None
    bank_name: str | None = None
    multiple_holders: bool | None = None
    calculated: list[str] = Field(default_factory=list)
    usage: str | None = None
    parties: list[AccountParty] = Field(default_factory=list)
    identifications: list[AccountIdentification] = Field(default_factory=list)


class AccountOwnershipsList(PowensModel):
    """Envelope for ``GET /users/{u}/account_ownerships``."""

    account_ownerships: list[AccountOwnership]


__all__ = [
    "AccountIdentification",
    "AccountOwnership",
    "AccountOwnershipsList",
    "AccountParty",
    "AccountPartyRole",
    "IdentityParty",
]
