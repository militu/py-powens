"""Investments resource.

Mirrors https://docs.powens.com/api-reference/products/wealth-aggregation/investments.
"""

from __future__ import annotations

from typing import Any

from powens.models.investment import (
    Investment,
    InvestmentHistoryValuesList,
    InvestmentsList,
)
from powens.resources._base import Resource
from powens.resources.pagination import AsyncOffsetPageIterator


class InvestmentsResource(Resource):
    """Endpoints under ``/users/{userId}/investments`` and ``/investments/*``."""

    def list(
        self,
        *,
        user_id: int | str = "me",
        account_id: int | None = None,
        connection_id: int | None = None,
        label: str | None = None,
        code: str | None = None,
        limit: int | None = None,
    ) -> AsyncOffsetPageIterator[Investment]:
        """Iterate over investments (lazy, offset-paged).

        The documented route aliases let you filter by account or
        connection without touching query parameters.
        """
        if account_id is not None:
            path = f"/users/{user_id}/accounts/{account_id}/investments"
        elif connection_id is not None:
            path = f"/users/{user_id}/connections/{connection_id}/investments"
        else:
            path = f"/users/{user_id}/investments"
        params: dict[str, Any] = {}
        if label is not None:
            params["label"] = label
        if code is not None:
            params["code"] = code
        return AsyncOffsetPageIterator[Investment](
            http=self._http,
            path=path,
            model=Investment,
            params=params,
            items_key="investments",
            limit=limit,
        )

    async def list_all(
        self,
        *,
        user_id: int | str = "me",
        account_id: int | None = None,
        connection_id: int | None = None,
        label: str | None = None,
        code: str | None = None,
    ) -> InvestmentsList:
        """Fetch investments with aggregated portfolio metrics.

        Returns the full envelope including ``valuation``, ``diff``,
        ``diff_percent``, ``prev_diff`` and ``calculated``.
        """
        if account_id is not None:
            path = f"/users/{user_id}/accounts/{account_id}/investments"
        elif connection_id is not None:
            path = f"/users/{user_id}/connections/{connection_id}/investments"
        else:
            path = f"/users/{user_id}/investments"
        params: dict[str, Any] = {}
        if label is not None:
            params["label"] = label
        if code is not None:
            params["code"] = code
        payload = await self._http.request_json("GET", path, params=params)
        return self._parse(InvestmentsList, payload)

    async def get(
        self,
        *,
        investment_id: int,
        user_id: int | str = "me",
    ) -> Investment:
        """Get a single investment by ID.

        The public reference documents ``GET /investments/{investmentId}``
        without a user scope, but live Powens deployments actually serve
        ``GET /users/{userId}/investments/{investmentId}`` — the SDK
        uses the user-scoped route which works end-to-end.
        """
        payload = await self._http.request_json(
            "GET", f"/users/{user_id}/investments/{investment_id}"
        )
        return self._parse(Investment, payload)

    async def history(
        self,
        *,
        investment_id: int,
        user_id: int | str = "me",
    ) -> InvestmentHistoryValuesList:
        """Get the history of an investment.

        Same user-scoping remark as :meth:`get`.
        """
        payload = await self._http.request_json(
            "GET", f"/users/{user_id}/investments/{investment_id}/history"
        )
        return self._parse(InvestmentHistoryValuesList, payload)


__all__ = ["InvestmentsResource"]
