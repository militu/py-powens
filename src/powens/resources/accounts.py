"""Bank accounts resource.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/bank-accounts.
"""

from __future__ import annotations

from typing import Any

from powens.models.account import BankAccount, BankAccountsList
from powens.resources._base import Resource
from powens.resources.pagination import AsyncOffsetPageIterator


class AccountsResource(Resource):
    """Endpoints under ``/users/{userId}/accounts/*``."""

    def list(
        self,
        *,
        user_id: int | str = "me",
        connection_id: int | None = None,
        include_all: bool = False,
        limit: int | None = None,
    ) -> AsyncOffsetPageIterator[BankAccount]:
        """Iterate over the user's bank accounts (lazy).

        When ``connection_id`` is provided, the path is the documented
        filtering alias
        ``/users/{userId}/connections/{connectionId}/accounts``.
        """
        path = (
            f"/users/{user_id}/connections/{connection_id}/accounts"
            if connection_id is not None
            else f"/users/{user_id}/accounts"
        )
        params: dict[str, Any] = {}
        if include_all:
            params["all"] = ""
        return AsyncOffsetPageIterator[BankAccount](
            http=self._http,
            path=path,
            model=BankAccount,
            params=params,
            items_key="accounts",
            limit=limit,
        )

    async def list_all(
        self,
        *,
        user_id: int | str = "me",
        connection_id: int | None = None,
        include_all: bool = False,
    ) -> BankAccountsList:
        """Fetch accounts + aggregated balances in a single call.

        Calls ``GET /users/{u}/accounts`` (or the connection alias) and
        returns the full envelope including ``balances`` and
        ``coming_balances`` associative maps.
        """
        path = (
            f"/users/{user_id}/connections/{connection_id}/accounts"
            if connection_id is not None
            else f"/users/{user_id}/accounts"
        )
        params: dict[str, Any] = {}
        if include_all:
            params["all"] = ""
        payload = await self._http.request_json("GET", path, params=params)
        return self._parse(BankAccountsList, payload)

    async def get(
        self,
        *,
        account_id: int,
        user_id: int | str = "me",
        include_all: bool = False,
    ) -> BankAccount:
        """Calls ``GET /users/{u}/accounts/{accountId}``."""
        params: dict[str, Any] = {}
        if include_all:
            params["all"] = ""
        payload = await self._http.request_json(
            "GET",
            f"/users/{user_id}/accounts/{account_id}",
            params=params,
        )
        return self._parse(BankAccount, payload)

    async def update(
        self,
        *,
        account_id: int,
        user_id: int | str = "me",
        display: bool | None = None,
        name: str | None = None,
        disabled: bool | None = None,
        bookmarked: bool | None = None,
        usage: str | None = None,
        include_all: bool = False,
    ) -> BankAccount:
        """Calls ``POST /users/{u}/accounts/{accountId}``.

        ``include_all=True`` (i.e. ``?all``) is required when enabling a
        disabled account, per the documented lifecycle.
        """
        body: dict[str, Any] = {}
        if display is not None:
            body["display"] = display
        if name is not None:
            body["name"] = name
        if disabled is not None:
            body["disabled"] = disabled
        if bookmarked is not None:
            body["bookmarked"] = bookmarked
        if usage is not None:
            body["usage"] = usage
        params: dict[str, Any] = {}
        if include_all:
            params["all"] = ""
        payload = await self._http.request_json(
            "POST",
            f"/users/{user_id}/accounts/{account_id}",
            params=params,
            json_body=body,
        )
        return self._parse(BankAccount, payload)


__all__ = ["AccountsResource"]
