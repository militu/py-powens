"""Pockets resource."""

from __future__ import annotations

from powens.models.pocket import Pocket, PocketsList
from powens.resources._base import Resource


class PocketsResource(Resource):
    """Endpoints under ``/users/{userId}/pockets`` and ``/pockets/*``."""

    async def list(
        self,
        *,
        user_id: int | str = "me",
        investment_id: int | None = None,
        account_id: int | None = None,
        connection_id: int | None = None,
    ) -> PocketsList:
        """Calls ``GET /users/{u}/pockets`` (or alias)."""
        if investment_id is not None:
            path = f"/users/{user_id}/investments/{investment_id}/pockets"
        elif account_id is not None:
            path = f"/users/{user_id}/accounts/{account_id}/pockets"
        elif connection_id is not None:
            path = f"/users/{user_id}/connections/{connection_id}/pockets"
        else:
            path = f"/users/{user_id}/pockets"
        payload = await self._http.request_json("GET", path)
        return self._parse(PocketsList, payload)

    async def get(self, *, pocket_id: int) -> Pocket:
        """Calls ``GET /pockets/{pocketId}``."""
        payload = await self._http.request_json("GET", f"/pockets/{pocket_id}")
        return self._parse(Pocket, payload)


__all__ = ["PocketsResource"]
