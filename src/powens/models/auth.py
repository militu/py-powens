"""Models for Powens authentication and webview flows.

Mirrors the canonical data model from
https://docs.powens.com/api-reference/overview/authentication and
https://docs.powens.com/api-reference/overview/webview.
"""

from __future__ import annotations

from enum import StrEnum

from powens.models.base import PowensModel


class AuthTokenType(StrEnum):
    """Value of ``AuthToken.type``. Documented as ``temporary`` or ``permanent``."""

    TEMPORARY = "temporary"
    PERMANENT = "permanent"


class AuthCodeRequestType(StrEnum):
    """Value accepted by the ``type`` query parameter of ``GET /auth/token/code``.

    Documented values, both destined for webview handoff.
    """

    SINGLE_ACCESS = "singleAccess"
    REQUEST_ACCESS = "requestAccess"


class AuthCodeType(StrEnum):
    """Value of ``AuthCode.type`` — the only documented value is ``temporary``."""

    TEMPORARY = "temporary"


class AuthCodeAccess(StrEnum):
    """Value of ``AuthCode.access`` — ``single`` or ``standard``."""

    SINGLE = "single"
    STANDARD = "standard"


class TokenTypeHeader(StrEnum):
    """Value of ``AuthTokenExchange.token_type`` — documented as ``Bearer``."""

    BEARER = "Bearer"


class AuthScope(StrEnum):
    """Documented Pay-product scopes for :class:`AuthServiceTokenRequest`.

    The SDK treats unknown scopes as plain strings; this enum only lists
    the values that appear in the reference, which is explicitly open.
    """

    PAYMENTS_ADMIN = "payments:admin"
    PAYMENTS_READ_ONLY = "payments:read-only"
    PAYMENTS_ALLOW_SENSITIVE = "payments:allow-sensitive"
    PAYMENTS_VALIDATE = "payments:validate"
    PAYMENTS_CANCEL = "payments:cancel"
    PAYMENTS_DEPRECATED = "payments"
    PAYMENT_LINKS_ADMIN = "payment-links:admin"


class AuthTokenInitRequest(PowensModel):
    """Request body for ``POST /auth/init``."""

    client_id: str | None = None
    client_secret: str | None = None


class AuthToken(PowensModel):
    """Response body for ``POST /auth/init`` and ``POST /auth/renew``.

    .. note::
       ``POST /auth/renew`` is actually documented as returning an
       :class:`AuthTokenExchange` (with ``access_token``/``token_type``).
       :class:`AuthToken` describes the shape returned by ``/auth/init``:
       ``auth_token``, ``type``, ``id_user``, ``expires_in``.
    """

    auth_token: str
    type: str
    id_user: int
    expires_in: int | None = None


class AuthCode(PowensModel):
    """Response body for ``GET /auth/token/code``."""

    code: str
    type: str
    access: str
    expires_in: int | None = None


class AuthTokenExchangeRequest(PowensModel):
    """Request body for ``POST /auth/token/access``."""

    client_id: str
    client_secret: str
    code: str
    grant_type: str = "authorization_code"


class AuthTokenExchange(PowensModel):
    """Response body for ``POST /auth/token/access`` and ``POST /auth/renew``."""

    access_token: str
    token_type: str


class AuthServiceTokenRequest(PowensModel):
    """Request body for ``POST /auth/token`` (service tokens).

    ``scope`` may be a single scope string or an array of scope strings;
    both forms are accepted by Powens.
    """

    client_id: str
    client_secret: str
    scope: str | list[str]
    grant_type: str = "client_credentials"


class AuthServiceToken(PowensModel):
    """Response body for ``POST /auth/token`` (service tokens)."""

    token: str
    scope: str


class AuthRenewRequest(PowensModel):
    """Request body for ``POST /auth/renew``."""

    client_id: str
    client_secret: str
    id_user: int
    grant_type: str = "client_credentials"
    revoke_previous: bool = False


# --- Webview helpers ------------------------------------------------------
# Webview URLs are not API responses; they are strings constructed by the
# SDK and opened in a browser. We type them minimally so callers get an
# explicit object rather than a bare string.


class AuthUrl(PowensModel):
    """A Powens URL (webview, webauth, etc.)."""

    url: str


class ManageUrl(AuthUrl):
    """URL for the ``/manage`` webview flow."""


class ConnectUrl(AuthUrl):
    """URL for the ``/connect`` webview flow."""


class ReconnectUrl(AuthUrl):
    """URL for the ``/reconnect`` webview flow."""

    id_connection: int | None = None


class PaymentWebviewUrl(AuthUrl):
    """URL for the ``/payment`` webview flow."""


class WebauthURL(PowensModel):
    """Response body for ``GET /webauth-url`` (API endpoint, not webview)."""

    url: str


# ``OTPRequest`` (historical SDK type) is kept as a compatibility shim: the
# real OTP submission happens through a regular Connection update with the
# connector fields. See :mod:`powens.resources.connections`.
class OTPRequest(PowensModel):
    id_connection: int
    otp: str


__all__ = [
    "AuthCode",
    "AuthCodeAccess",
    "AuthCodeRequestType",
    "AuthCodeType",
    "AuthRenewRequest",
    "AuthScope",
    "AuthServiceToken",
    "AuthServiceTokenRequest",
    "AuthToken",
    "AuthTokenExchange",
    "AuthTokenExchangeRequest",
    "AuthTokenInitRequest",
    "AuthTokenType",
    "AuthUrl",
    "ConnectUrl",
    "ManageUrl",
    "OTPRequest",
    "PaymentWebviewUrl",
    "ReconnectUrl",
    "TokenTypeHeader",
    "WebauthURL",
]
