"""Currencies resource.

https://docs.powens.com/api-reference/products/data-aggregation/currencies
"""

from __future__ import annotations

from powens.models.currency import CurrenciesList
from powens.resources._base import Resource


class CurrenciesResource(Resource):
    """Endpoints under ``/currencies``."""

    async def list(self) -> CurrenciesList:
        """Calls ``GET /currencies``. No authentication required."""
        payload = await self._http.request_json("GET", "/currencies", auth_required=False)
        return self._parse(CurrenciesList, payload)


__all__ = ["CurrenciesResource"]
