"""Webview URL builders.

The Powens webview is served from a separate host
(``https://webview.powens.com``) and takes the API domain as a query
parameter. This module assembles the exact URLs documented in
https://docs.powens.com/api-reference/overview/webview — no HTTP call is
issued; the result is a plain URL string wrapped in a typed model.

Four flows are documented and exposed here: ``connect``, ``reconnect``,
``manage``, ``payment``. The deprecated ``transfer`` flow is intentionally
not wrapped.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import quote, urlencode

from powens.models.auth import ConnectUrl, ManageUrl, PaymentWebviewUrl, ReconnectUrl

WEBVIEW_BASE_URL = "https://webview.powens.com"
DEFAULT_LANG = "en"


class WebviewResource:
    """URL builder for the Powens webview flows.

    The builder needs to know the **API domain** (e.g.
    ``example.biapi.pro``) to populate the ``domain`` query parameter
    required on every flow. The SDK derives the domain from the client's
    ``base_url``; callers with a non-standard base may pass an explicit
    ``api_domain``.
    """

    def __init__(self, *, api_domain: str) -> None:
        self._api_domain = api_domain

    # ------------------------------------------------------------------
    # connect
    # ------------------------------------------------------------------

    def connect_url(
        self,
        *,
        client_id: str,
        redirect_uri: str,
        lang: str = DEFAULT_LANG,
        code: str | None = None,
        state: str | None = None,
        connector_ids: Iterable[int | str] | None = None,
        connector_uuids: Iterable[str] | None = None,
        connector_capabilities: Iterable[str] | None = None,
        account_ibans: Iterable[str] | None = None,
        account_types: Iterable[str] | None = None,
        max_connections: int | None = None,
        extra_params: Mapping[str, str] | None = None,
    ) -> ConnectUrl:
        """Build a URL for the ``/connect`` webview flow.

        ``extra_params`` can be used for connector-field prefilling
        (e.g. ``{"<uuid>.website": "pro"}``). Keys are sent as-is.
        """
        params: list[tuple[str, str]] = [
            ("domain", self._api_domain),
            ("client_id", client_id),
            ("redirect_uri", redirect_uri),
        ]
        if code is not None:
            params.append(("code", code))
        if state is not None:
            params.append(("state", state))
        if connector_ids is not None:
            params.append(("connector_ids", ",".join(str(x) for x in connector_ids)))
        if connector_uuids is not None:
            params.append(("connector_uuids", ",".join(connector_uuids)))
        if connector_capabilities is not None:
            params.append(("connector_capabilities", ",".join(connector_capabilities)))
        if account_ibans is not None:
            params.append(("account_ibans", ",".join(account_ibans)))
        if account_types is not None:
            params.append(("account_types", ",".join(account_types)))
        if max_connections is not None:
            params.append(("max_connections", str(max_connections)))
        if extra_params:
            for k, v in extra_params.items():
                params.append((k, v))
        return ConnectUrl(url=_build_url(lang=lang, flow="connect", params=params))

    # ------------------------------------------------------------------
    # reconnect
    # ------------------------------------------------------------------

    def reconnect_url(
        self,
        *,
        client_id: str,
        redirect_uri: str,
        code: str,
        connection_id: int,
        lang: str = DEFAULT_LANG,
        state: str | None = None,
        reset_credentials: bool = False,
        connection_sources: Iterable[str] | None = None,
    ) -> ReconnectUrl:
        """Build a URL for the ``/reconnect`` webview flow."""
        params: list[tuple[str, str]] = [
            ("domain", self._api_domain),
            ("client_id", client_id),
            ("redirect_uri", redirect_uri),
            ("code", code),
            ("connection_id", str(connection_id)),
        ]
        if state is not None:
            params.append(("state", state))
        if reset_credentials:
            params.append(("reset_credentials", "true"))
        if connection_sources is not None:
            params.append(("connection_sources", ",".join(connection_sources)))
        return ReconnectUrl(
            url=_build_url(lang=lang, flow="reconnect", params=params),
            id_connection=connection_id,
        )

    # ------------------------------------------------------------------
    # manage
    # ------------------------------------------------------------------

    def manage_url(
        self,
        *,
        client_id: str,
        code: str,
        lang: str = DEFAULT_LANG,
        connection_id: int | None = None,
        redirect_uri: str | None = None,
        state: str | None = None,
        connector_capabilities: Iterable[str] | None = None,
        account_types: Iterable[str] | None = None,
    ) -> ManageUrl:
        """Build a URL for the ``/manage`` webview flow.

        ``redirect_uri`` is optional on this flow; when omitted the
        webview simply renders without a close button.
        """
        params: list[tuple[str, str]] = [
            ("domain", self._api_domain),
            ("client_id", client_id),
            ("code", code),
        ]
        if connection_id is not None:
            params.append(("connection_id", str(connection_id)))
        if redirect_uri is not None:
            params.append(("redirect_uri", redirect_uri))
        if state is not None:
            params.append(("state", state))
        if connector_capabilities is not None:
            params.append(("connector_capabilities", ",".join(connector_capabilities)))
        if account_types is not None:
            params.append(("account_types", ",".join(account_types)))
        return ManageUrl(url=_build_url(lang=lang, flow="manage", params=params))

    # ------------------------------------------------------------------
    # payment
    # ------------------------------------------------------------------

    def payment_url(
        self,
        *,
        client_id: str,
        redirect_uri: str,
        code: str,
        payment_id: str,
        lang: str = DEFAULT_LANG,
        state: str | None = None,
    ) -> PaymentWebviewUrl:
        """Build a URL for the ``/payment`` webview flow."""
        params: list[tuple[str, str]] = [
            ("domain", self._api_domain),
            ("client_id", client_id),
            ("redirect_uri", redirect_uri),
            ("code", code),
            ("payment_id", payment_id),
        ]
        if state is not None:
            params.append(("state", state))
        return PaymentWebviewUrl(url=_build_url(lang=lang, flow="payment", params=params))


def _build_url(*, lang: str, flow: str, params: list[tuple[str, str]]) -> str:
    safe_lang = quote(lang, safe="")
    safe_flow = quote(flow, safe="")
    query = urlencode(params, doseq=False, quote_via=quote)
    return f"{WEBVIEW_BASE_URL}/{safe_lang}/{safe_flow}?{query}"


def _coerce_param(value: Any) -> str:
    return str(value)


__all__ = ["DEFAULT_LANG", "WEBVIEW_BASE_URL", "WebviewResource"]
