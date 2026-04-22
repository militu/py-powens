"""Indicators resource."""

from __future__ import annotations

from powens.models.indicator import UserIndicators
from powens.resources._base import Resource


class IndicatorsResource(Resource):
    """Endpoints under ``/users/{userId}/indicators``."""

    async def get(self, *, user_id: int | str = "me") -> UserIndicators:
        """Calls ``GET /users/{u}/indicators``."""
        payload = await self._http.request_json("GET", f"/users/{user_id}/indicators")
        return self._parse(UserIndicators, payload)


__all__ = ["IndicatorsResource"]
