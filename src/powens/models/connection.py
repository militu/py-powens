"""Connection, ConnectionSource and related models.

Mirrors https://docs.powens.com/api-reference/user-connections/connections.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from powens.models.base import PowensModel
from powens.models.connector import Connector, ConnectorField


class ConnectionState(StrEnum):
    """Documented values for :attr:`Connection.state`.

    Per the spec, ``state = null`` indicates a successful synchronization.
    The enum below lists every documented error state; unknown values must
    fall back to a non-resolvable generic case.
    """

    SCA_REQUIRED = "SCARequired"
    WEBAUTH_REQUIRED = "webauthRequired"
    ADDITIONAL_INFORMATION_NEEDED = "additionalInformationNeeded"
    DECOUPLED = "decoupled"
    VALIDATING = "validating"
    ACTION_NEEDED = "actionNeeded"
    PASSWORD_EXPIRED = "passwordExpired"
    WRONG_PASS = "wrongpass"
    RATE_LIMITING = "rateLimiting"
    WEBSITE_UNAVAILABLE = "websiteUnavailable"
    BUG = "bug"
    NOT_SUPPORTED = "notSupported"


class Connection(PowensModel):
    """A Powens connection (link between a user and a connector)."""

    id: int
    id_user: int | None = None
    id_connector: int
    # Deprecated fields kept for fidelity with the response payload.
    id_provider: int | None = None
    id_bank: int | None = None
    state: str | None = None
    error: str | None = None  # (Deprecated) duplicate of ``state``.
    error_message: str | None = None
    fields: list[ConnectorField] | None = None
    last_update: datetime | None = None
    created: datetime | None = None
    active: bool
    last_push: datetime | None = None
    expire: datetime | None = None
    connector_uuid: str
    next_try: datetime | None = None
    # Available expands — populated only when requested.
    connector: Connector | None = None


class ConnectionsList(PowensModel):
    """Envelope for ``GET /users/{userId}/connections``."""

    connections: list[Connection]


class ConnectionRequest(PowensModel):
    """Request body for ``POST /users/{userId}/connections``.

    Either ``id_connector`` or ``connector_uuid`` must be supplied.
    Additional connector-field values are sent on the same body using
    the field's ``name`` as key — these are passed through
    ``extra_fields`` in the resource method.
    """

    id_connector: int | None = None
    connector_uuid: str | None = None
    source: str | None = None


class ConnectionUpdateRequest(PowensModel):
    """Request body for ``POST /users/{userId}/connections/{id}``.

    Also used to submit additional information (OTP / new password)
    during an ``additionalInformationNeeded`` state by supplying the
    relevant connector fields alongside these flags (passed through
    ``extra_fields`` at the resource level).
    """

    source: str | None = None
    active: bool | None = None
    expire: datetime | None = None
    resume: bool | None = None
    refresh_auth: bool | None = None


class ConnectionSource(PowensModel):
    """A source linked to a connection."""

    id: int
    id_connection: int
    id_connector_source: int
    name: str
    last_update: datetime | None = None
    disabled: datetime | None = None
    created: datetime
    state: str | None = None
    access_expire: datetime | None = None
    expire: datetime | None = None
    next_try: datetime | None = None


class ConnectionSourcesList(PowensModel):
    """Envelope for ``GET /users/{u}/connections/{id}/sources``."""

    sources: list[ConnectionSource]


class ConnectionSourceUpdateRequest(PowensModel):
    """Request body for ``POST /users/{u}/connections/{id}/sources/{sid}``."""

    disabled: bool | None = None


__all__ = [
    "Connection",
    "ConnectionRequest",
    "ConnectionSource",
    "ConnectionSourceUpdateRequest",
    "ConnectionSourcesList",
    "ConnectionState",
    "ConnectionUpdateRequest",
    "ConnectionsList",
]
