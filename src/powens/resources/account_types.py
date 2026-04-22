"""Bank account types resource.

https://docs.powens.com/api-reference/products/data-aggregation/bank-account-types
"""

from __future__ import annotations

from powens.models.account_type import AccountType, AccountTypesList
from powens.resources._base import Resource


class AccountTypesResource(Resource):
    """Endpoints under ``/account_types``."""

    async def list(self) -> AccountTypesList:
        """Calls ``GET /account_types``."""
        payload = await self._http.request_json("GET", "/account_types", auth_required=False)
        return self._parse(AccountTypesList, payload)

    async def get(self, *, type_id: int) -> AccountType:
        """Calls ``GET /account_types/{typeId}``."""
        payload = await self._http.request_json(
            "GET", f"/account_types/{type_id}", auth_required=False
        )
        return self._parse(AccountType, payload)


__all__ = ["AccountTypesResource"]
