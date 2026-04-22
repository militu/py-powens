"""Bank transactions resource.

Mirrors https://docs.powens.com/api-reference/products/data-aggregation/bank-transactions.

The list endpoint requires an explicit ``limit`` parameter and supports
relational (cursor) pagination through ``_links.next.href``. The SDK's
:meth:`list` method returns an :class:`AsyncCursorPageIterator` that
follows the cursor URL verbatim as the documentation requires.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date as _date
from typing import Any

from powens.models.transaction import Transaction, TransactionsList
from powens.resources._base import Resource
from powens.resources.pagination import AsyncCursorPageIterator


class TransactionsResource(Resource):
    """Endpoints under ``/users/{userId}/transactions``."""

    def list(
        self,
        *,
        user_id: int | str = "me",
        account_id: int | None = None,
        connection_id: int | None = None,
        limit: int = 1000,
        include_all: bool = False,
        income: bool | None = None,
        deleted: bool | None = None,
        filter: str | None = None,
        min_date: _date | str | None = None,
        max_date: _date | str | None = None,
        wording: str | None = None,
        min_value: Any | None = None,
        max_value: Any | None = None,
        search: str | None = None,
        value: Any | None = None,
        last_update: str | None = None,
        expand: str | None = None,
    ) -> AsyncCursorPageIterator[Transaction]:
        """Iterate over transactions using relational pagination.

        The documented ``limit`` parameter is required; the SDK defaults
        it to the maximum of 1000 but callers can override.

        When ``account_id`` / ``connection_id`` is set, the SDK uses the
        corresponding route alias (``/accounts/{id}/transactions`` or
        ``/connections/{id}/transactions``).
        """
        if account_id is not None:
            path = f"/users/{user_id}/accounts/{account_id}/transactions"
        elif connection_id is not None:
            path = f"/users/{user_id}/connections/{connection_id}/transactions"
        else:
            path = f"/users/{user_id}/transactions"

        params: dict[str, Any] = {"limit": limit}
        if include_all:
            params["all"] = ""
        if income is not None:
            params["income"] = str(income).lower()
        if deleted is not None:
            params["deleted"] = str(deleted).lower()
        if filter is not None:
            params["filter"] = filter
        if min_date is not None:
            params["min_date"] = min_date.isoformat() if isinstance(min_date, _date) else min_date
        if max_date is not None:
            params["max_date"] = max_date.isoformat() if isinstance(max_date, _date) else max_date
        if wording is not None:
            params["wording"] = wording
        if min_value is not None:
            params["min_value"] = min_value
        if max_value is not None:
            params["max_value"] = max_value
        if search is not None:
            params["search"] = search
        if value is not None:
            params["value"] = value
        if last_update is not None:
            params["last_update"] = last_update
        if expand is not None:
            params["expand"] = expand

        return AsyncCursorPageIterator[Transaction](
            http=self._http,
            path=path,
            model=Transaction,
            params=params,
            items_key="transactions",
            limit=limit,
        )

    async def list_page(
        self,
        *,
        user_id: int | str = "me",
        account_id: int | None = None,
        connection_id: int | None = None,
        limit: int = 1000,
        **kwargs: Any,
    ) -> TransactionsList:
        """Fetch a single page and return the complete envelope.

        Useful when callers need the ``first_date`` / ``last_date`` /
        ``result_min_date`` / ``result_max_date`` fields the envelope
        exposes alongside ``transactions``.
        """
        if account_id is not None:
            path = f"/users/{user_id}/accounts/{account_id}/transactions"
        elif connection_id is not None:
            path = f"/users/{user_id}/connections/{connection_id}/transactions"
        else:
            path = f"/users/{user_id}/transactions"
        params: dict[str, Any] = {"limit": limit}
        for key, val in kwargs.items():
            if val is None:
                continue
            if isinstance(val, _date):
                params[key] = val.isoformat()
            elif isinstance(val, bool):
                params[key] = str(val).lower()
            else:
                params[key] = val
        payload = await self._http.request_json("GET", path, params=params)
        return self._parse(TransactionsList, payload)

    async def get(
        self,
        *,
        transaction_id: int,
        user_id: int | str = "me",
    ) -> Transaction:
        """Calls ``GET /users/{u}/transactions/{transactionId}``."""
        payload = await self._http.request_json(
            "GET",
            f"/users/{user_id}/transactions/{transaction_id}",
        )
        return self._parse(Transaction, payload)

    async def update(
        self,
        *,
        transaction_id: int,
        user_id: int | str = "me",
        wording: str | None = None,
        application_date: _date | str | None = None,
        categories: Sequence[dict[str, Any]] | None = None,
        comment: str | None = None,
        active: bool | None = None,
    ) -> Transaction:
        """Calls ``POST /users/{u}/transactions/{transactionId}``."""
        body: dict[str, Any] = {}
        if wording is not None:
            body["wording"] = wording
        if application_date is not None:
            body["application_date"] = (
                application_date.isoformat()
                if isinstance(application_date, _date)
                else application_date
            )
        if categories is not None:
            body["categories"] = categories
        if comment is not None:
            body["comment"] = comment
        if active is not None:
            body["active"] = active
        payload = await self._http.request_json(
            "POST",
            f"/users/{user_id}/transactions/{transaction_id}",
            json_body=body,
        )
        return self._parse(Transaction, payload)


__all__ = ["TransactionsResource"]
