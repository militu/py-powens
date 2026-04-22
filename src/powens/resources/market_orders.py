"""Market orders resource."""

from __future__ import annotations

from powens.models.market_order import MarketOrder, MarketOrdersList
from powens.resources._base import Resource


class MarketOrdersResource(Resource):
    """Endpoints under ``/users/{userId}/marketorders`` and ``/marketorders/*``."""

    async def list(
        self,
        *,
        user_id: int | str = "me",
        account_id: int | None = None,
        connection_id: int | None = None,
    ) -> MarketOrdersList:
        """Calls ``GET /users/{u}/marketorders`` (or alias)."""
        if account_id is not None:
            path = f"/users/{user_id}/accounts/{account_id}/marketorders"
        elif connection_id is not None:
            path = f"/users/{user_id}/connections/{connection_id}/marketorders"
        else:
            path = f"/users/{user_id}/marketorders"
        payload = await self._http.request_json("GET", path)
        return self._parse(MarketOrdersList, payload)

    async def get(self, *, market_order_id: int) -> MarketOrder:
        """Calls ``GET /marketorders/{marketOrderId}``."""
        payload = await self._http.request_json("GET", f"/marketorders/{market_order_id}")
        return self._parse(MarketOrder, payload)


__all__ = ["MarketOrdersResource"]
