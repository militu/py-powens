"""Connector data model and sub-models.

Mirrors https://docs.powens.com/api-reference/connectors. Every field
documented under the ``Connector`` object and its related types is
present here; forward-compatibility is handled through open enums
(``StrEnum``) with a tolerant parse on unknown strings.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from powens.models.base import PowensModel


class AuthMechanism(StrEnum):
    """Documented values for ``auth_mechanism``.

    The spec marks this enum as open; unknown values are preserved as
    strings on the consuming ``str`` field.
    """

    CREDENTIALS = "credentials"
    WEBAUTH = "webauth"


class ConnectorFieldType(StrEnum):
    """Documented values for :attr:`ConnectorField.type`."""

    TEXT = "text"
    PASSWORD = "password"
    DATE = "date"
    LIST = "list"


class ProvidingPayerAccount(StrEnum):
    """Documented values for :attr:`PaymentSettings.providing_payer_account`."""

    NOT_USED = "not_used"
    OPTIONAL = "optional"
    MANDATORY = "mandatory"


class Product(StrEnum):
    """Documented product identifiers."""

    BANK = "bank"
    WEALTH = "wealth"
    BILL = "bill"
    PAY = "pay"


class ConnectorCountry(PowensModel):
    """A country listed on ``Connector.countries`` (expanded)."""

    id: str
    name: str


class ConnectorFieldValueOption(PowensModel):
    """One entry of ``ConnectorField.values`` (list-type fields)."""

    label: str
    value: str


class ConnectorField(PowensModel):
    """A connector form field (initial credentials / update)."""

    name: str
    connector_sources: list[str] = Field(default_factory=list)
    auth_mechanisms: list[str] = Field(default_factory=list)
    type: str
    label: str
    required: bool
    regex: str | None = None
    values: list[ConnectorFieldValueOption] | None = None


class ConnectorPaymentField(PowensModel):
    """A payment-validation form field (see `payment_fields` expand)."""

    name: str
    auth_mechanisms: list[str] = Field(default_factory=list)
    type: str
    label: str
    required: bool
    regex: str | None = None
    values: list[ConnectorFieldValueOption] | None = None


class PaymentAppToAppUsed(PowensModel):
    """Per-platform flag for payment app-to-app support."""

    android: bool | None = None
    ios: bool | None = None


class PaymentAmount(PowensModel):
    """Amount limits keyed by execution date type."""

    first_open_day: Decimal | None = None
    instant: Decimal | None = None
    deferred: Decimal | None = None
    periodic: Decimal | None = None


class PaymentSettings(PowensModel):
    """Information about the ``Pay`` product feature on a connector.

    Only present when the Pay product is enabled on the connector.
    """

    available_validate_mechanisms: list[str] = Field(default_factory=list)
    beneficiary_types: list[str] = Field(default_factory=list)
    execution_date_types: list[str] = Field(default_factory=list)
    execution_frequencies: list[str] = Field(default_factory=list)
    maximum_number_of_instructions: int | None = None
    providing_payer_account: str | None = None
    partial_status_tracking: list[str] = Field(default_factory=list)
    is_app_to_app_used: PaymentAppToAppUsed | None = None
    bank_provides_payer_account: bool | None = None
    bank_provides_payer_label: bool | None = None
    transfer_date_types_where_trusted_beneficiary_required: list[str] = Field(default_factory=list)
    cancellation_available: bool | None = None
    minimum_amount: PaymentAmount | None = None
    maximum_amount: PaymentAmount | None = None
    minimum_date_delta_days: Decimal | None = None
    maximum_date_delta_days: Decimal | None = None


class ConnectorSource(PowensModel):
    """Per the ``ConnectorSource`` object spec."""

    id: int
    id_connector: int
    name: str
    auth_mechanism: str | None = None
    available_auth_mechanisms: list[str] = Field(default_factory=list)
    disabled: datetime | None = None
    priority: int
    account_usages: list[str] = Field(default_factory=list)


class ConnectorSourcesList(PowensModel):
    """Envelope for ``GET /connectors/{uuid}/sources``."""

    sources: list[ConnectorSource]


class ConnectorSourceUpdateRequest(PowensModel):
    """Request body for ``PUT /connectors/{uuid}/sources/{sourceId}``."""

    auth_mechanism: str | None = None
    disabled: datetime | None = None


class Connector(PowensModel):
    """A Powens connector (bank or provider).

    All fields documented under ``Connector`` are present. Expanded
    relations (``sources``, ``fields``, ``payment_fields``, ``countries``,
    ``urls``) are optional here: they only appear when requested via
    the ``expand`` query parameter.
    """

    id: int
    uuid: str
    name: str
    hidden: bool | None = None
    charged: bool
    code: str | None = None
    beta: bool
    color: str | None = None
    slug: str | None = None
    # ``sync_frequency`` is documented as deprecated; kept for fidelity.
    sync_frequency: Decimal | None = None
    months_to_fetch: int | None = None
    auth_mechanism: str | None = None
    available_auth_mechanisms: list[str] = Field(default_factory=list)
    transfer_mechanism: str | None = None
    siret: str | None = None
    restricted: bool
    capabilities: list[str] = Field(default_factory=list)
    account_usages: list[str] = Field(default_factory=list)
    payment_settings: PaymentSettings | None = None
    products: list[str] = Field(default_factory=list)
    # Available expands — optional, not returned by default
    sources: list[ConnectorSource] | None = None
    fields: list[ConnectorField] | None = None
    payment_fields: list[ConnectorPaymentField] | None = None
    countries: list[ConnectorCountry] | None = None
    urls: list[str] | None = None


class ConnectorsList(PowensModel):
    """Envelope for ``GET /connectors``.

    The documented deprecated alias ``banks`` is not modelled; it was
    only used on deprecated routes the SDK does not expose.
    """

    connectors: list[Connector]


class ConnectorUpdateRequest(PowensModel):
    """Request body for ``PUT /connectors/{uuid}``.

    ``sync_periodicity`` is documented as deprecated but kept for
    fidelity.
    """

    hidden: bool | None = None
    sync_periodicity: Decimal | None = None


__all__ = [
    "AuthMechanism",
    "Connector",
    "ConnectorCountry",
    "ConnectorField",
    "ConnectorFieldType",
    "ConnectorFieldValueOption",
    "ConnectorPaymentField",
    "ConnectorSource",
    "ConnectorSourceUpdateRequest",
    "ConnectorSourcesList",
    "ConnectorUpdateRequest",
    "ConnectorsList",
    "PaymentAmount",
    "PaymentAppToAppUsed",
    "PaymentSettings",
    "Product",
    "ProvidingPayerAccount",
]
