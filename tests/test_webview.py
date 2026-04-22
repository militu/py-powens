"""Tests for the webview URL builder.

The webview is served from ``https://webview.powens.com/{lang}/{flow}``
with the API domain as a query parameter. We do not issue HTTP requests
here; the resource is a pure URL builder.
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from powens import PowensClient
from powens.resources.webview import WEBVIEW_BASE_URL, WebviewResource


def _qs(url: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(url).query, keep_blank_values=True)


def test_connect_url_minimal() -> None:
    wv = WebviewResource(api_domain="example.biapi.pro")
    built = wv.connect_url(
        client_id="cid",
        redirect_uri="https://app/cb",
    )
    parsed = urlparse(built.url)
    assert parsed.scheme == "https"
    assert parsed.netloc == urlparse(WEBVIEW_BASE_URL).netloc
    assert parsed.path == "/en/connect"
    q = _qs(built.url)
    assert q["domain"] == ["example.biapi.pro"]
    assert q["client_id"] == ["cid"]
    assert q["redirect_uri"] == ["https://app/cb"]


def test_connect_url_all_options() -> None:
    wv = WebviewResource(api_domain="example.biapi.pro")
    built = wv.connect_url(
        client_id="cid",
        redirect_uri="https://app/cb",
        lang="fr",
        code="tempcode",
        state="xyz",
        connector_ids=[1, 2, 3],
        connector_uuids=["uuid1", "uuid2"],
        connector_capabilities=["bank", "bankwealth"],
        account_ibans=["FR76xxxx", "FR77yyyy"],
        account_types=["checking", "card"],
        max_connections=5,
        extra_params={"uuid-x.website": "pro"},
    )
    parsed = urlparse(built.url)
    assert parsed.path == "/fr/connect"
    q = _qs(built.url)
    assert q["state"] == ["xyz"]
    assert q["code"] == ["tempcode"]
    assert q["connector_ids"] == ["1,2,3"]
    assert q["connector_uuids"] == ["uuid1,uuid2"]
    assert q["connector_capabilities"] == ["bank,bankwealth"]
    assert q["account_ibans"] == ["FR76xxxx,FR77yyyy"]
    assert q["account_types"] == ["checking,card"]
    assert q["max_connections"] == ["5"]
    assert q["uuid-x.website"] == ["pro"]


def test_reconnect_url_required_params() -> None:
    wv = WebviewResource(api_domain="example.biapi.pro")
    built = wv.reconnect_url(
        client_id="cid",
        redirect_uri="https://app/cb",
        code="tempcode",
        connection_id=7,
        reset_credentials=True,
        connection_sources=["openapi"],
    )
    assert built.id_connection == 7
    parsed = urlparse(built.url)
    assert parsed.path == "/en/reconnect"
    q = _qs(built.url)
    assert q["connection_id"] == ["7"]
    assert q["code"] == ["tempcode"]
    assert q["reset_credentials"] == ["true"]
    assert q["connection_sources"] == ["openapi"]


def test_manage_url_without_redirect_uri() -> None:
    wv = WebviewResource(api_domain="example.biapi.pro")
    built = wv.manage_url(client_id="cid", code="tempcode", connection_id=42)
    parsed = urlparse(built.url)
    assert parsed.path == "/en/manage"
    q = _qs(built.url)
    assert q["client_id"] == ["cid"]
    assert q["code"] == ["tempcode"]
    assert q["connection_id"] == ["42"]
    assert "redirect_uri" not in q


def test_payment_url() -> None:
    wv = WebviewResource(api_domain="example.biapi.pro")
    built = wv.payment_url(
        client_id="cid",
        redirect_uri="https://app/cb",
        code="svc",
        payment_id="pay-99",
        state="st",
    )
    parsed = urlparse(built.url)
    assert parsed.path == "/en/payment"
    q = _qs(built.url)
    assert q["payment_id"] == ["pay-99"]
    assert q["state"] == ["st"]


def test_client_infers_api_domain_from_base_url() -> None:
    client = PowensClient(base_url="https://example.biapi.pro/2.0", access_token="t")
    built = client.webview.connect_url(client_id="cid", redirect_uri="https://app/cb")
    q = _qs(built.url)
    assert q["domain"] == ["example.biapi.pro"]


def test_client_allows_overriding_api_domain() -> None:
    client = PowensClient(
        base_url="https://internal-proxy/2.0",
        access_token="t",
        api_domain="public.biapi.pro",
    )
    built = client.webview.manage_url(client_id="cid", code="c")
    q = _qs(built.url)
    assert q["domain"] == ["public.biapi.pro"]
