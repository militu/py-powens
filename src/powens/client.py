"""Public entry point of the SDK: :class:`PowensClient`.

The client composes:
- an internal :class:`HTTPClient` (retry + circuit breaker + error mapping),
- a set of resource wrappers (auth, connections, accounts, investments,
  transactions).

Design note: composition over inheritance. Users never subclass the client —
they either configure it at construction time or inject an ``httpx.AsyncClient``
/ ``httpx.AsyncBaseTransport`` for tests.
"""

from __future__ import annotations

from types import TracebackType
from typing import Self
from urllib.parse import urlparse

import httpx

from powens._http.circuit import CircuitBreaker
from powens._http.client import DEFAULT_TIMEOUT_SECONDS, HTTPClient
from powens._http.retry import RetryPolicy
from powens.resources.account_ownerships import AccountOwnershipsResource
from powens.resources.account_types import AccountTypesResource
from powens.resources.accounts import AccountsResource
from powens.resources.auth import AuthResource
from powens.resources.balances import BalancesResource
from powens.resources.connections import ConnectionsResource
from powens.resources.connectors import ConnectorsResource
from powens.resources.currencies import CurrenciesResource
from powens.resources.indicators import IndicatorsResource
from powens.resources.investments import InvestmentsResource
from powens.resources.loan_amortizations import LoanAmortizationsResource
from powens.resources.market_orders import MarketOrdersResource
from powens.resources.pockets import PocketsResource
from powens.resources.transactions import TransactionsResource
from powens.resources.users import UsersResource
from powens.resources.webview import WebviewResource


class PowensClient:
    """High-level Powens API client.

    Example:
        >>> async with PowensClient(
        ...     base_url="https://demo.biapi.pro/2.0",
        ...     access_token="...",
        ... ) as client:
        ...     connections = [c async for c in client.connections.list()]
    """

    def __init__(
        self,
        *,
        base_url: str,
        access_token: str | None = None,
        user_agent: str = "py-powens",
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        http_client: httpx.AsyncClient | None = None,
        api_domain: str | None = None,
    ) -> None:
        self._http = HTTPClient(
            base_url=base_url,
            access_token=access_token,
            user_agent=user_agent,
            timeout=timeout,
            retry_policy=retry_policy,
            circuit_breaker=circuit_breaker,
            transport=transport,
            http_client=http_client,
        )
        resolved_domain = api_domain or _infer_api_domain(base_url)
        self.auth = AuthResource(self._http)
        self.users = UsersResource(self._http)
        self.connectors = ConnectorsResource(self._http)
        self.connections = ConnectionsResource(self._http)
        self.accounts = AccountsResource(self._http)
        self.account_types = AccountTypesResource(self._http)
        self.currencies = CurrenciesResource(self._http)
        self.investments = InvestmentsResource(self._http)
        self.market_orders = MarketOrdersResource(self._http)
        self.pockets = PocketsResource(self._http)
        self.loan_amortizations = LoanAmortizationsResource(self._http)
        self.balances = BalancesResource(self._http)
        self.account_ownerships = AccountOwnershipsResource(self._http)
        self.indicators = IndicatorsResource(self._http)
        self.transactions = TransactionsResource(self._http)
        self.webview = WebviewResource(api_domain=resolved_domain)

    @property
    def access_token(self) -> str | None:
        return self._http.access_token

    def set_access_token(self, token: str | None) -> None:
        """Update the bearer token used on subsequent requests."""
        self._http.set_access_token(token)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Release the underlying HTTP resources."""
        await self._http.aclose()


def _infer_api_domain(base_url: str) -> str:
    """Extract the Powens API domain from a base URL.

    Example: ``https://example.biapi.pro/2.0`` → ``example.biapi.pro``.
    Falls back to the full netloc when the URL cannot be parsed.
    """
    parsed = urlparse(base_url)
    return parsed.netloc or base_url


__all__ = ["PowensClient"]
