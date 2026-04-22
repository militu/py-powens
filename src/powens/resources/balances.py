"""Balances resource."""

from __future__ import annotations

from datetime import date as _date
from typing import Any

from powens.models.balance import BalanceGroupsList
from powens.resources._base import Resource


class BalancesResource(Resource):
    """Endpoints under ``/users/{userId}/accounts/{accountId}/balances``."""

    async def get(
        self,
        *,
        account_id: int,
        user_id: int | str = "me",
        min_date: _date | str | None = None,
        max_date: _date | str | None = None,
    ) -> BalanceGroupsList:
        """Calls ``GET /users/{u}/accounts/{accountId}/balances``."""
        params: dict[str, Any] = {}
        if min_date is not None:
            params["min_date"] = min_date.isoformat() if isinstance(min_date, _date) else min_date
        if max_date is not None:
            params["max_date"] = max_date.isoformat() if isinstance(max_date, _date) else max_date
        payload = await self._http.request_json(
            "GET",
            f"/users/{user_id}/accounts/{account_id}/balances",
            params=params,
        )
        return self._parse(BalanceGroupsList, payload)


__all__ = ["BalancesResource"]
