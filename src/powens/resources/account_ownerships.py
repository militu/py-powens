"""Account ownerships resource."""

from __future__ import annotations

from powens.models.account_ownership import AccountOwnershipsList
from powens.resources._base import Resource


class AccountOwnershipsResource(Resource):
    """Endpoints under ``/users/{userId}/account_ownerships``."""

    async def list(
        self,
        *,
        user_id: int | str = "me",
    ) -> AccountOwnershipsList:
        """Calls ``GET /users/{u}/account_ownerships``.

        Feature-gated on the Powens side (contact Powens to enable).
        """
        payload = await self._http.request_json("GET", f"/users/{user_id}/account_ownerships")
        return self._parse(AccountOwnershipsList, payload)


__all__ = ["AccountOwnershipsResource"]
