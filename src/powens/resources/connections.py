"""Connections resource.

Wraps every endpoint documented under
https://docs.powens.com/api-reference/user-connections/connections,
including connection sources and synchronization logs.
"""

from __future__ import annotations

from typing import Any

from powens.models.auth import WebauthURL
from powens.models.connection import (
    Connection,
    ConnectionsList,
    ConnectionSource,
    ConnectionSourcesList,
)
from powens.resources._base import Resource
from powens.resources.pagination import AsyncOffsetPageIterator


class ConnectionsResource(Resource):
    """Endpoints under ``/users/{userId}/connections/*`` and ``/webauth*``."""

    # ------------------------------------------------------------------
    # Core CRUD + sync
    # ------------------------------------------------------------------

    async def create(
        self,
        *,
        user_id: int | str = "me",
        id_connector: int | None = None,
        connector_uuid: str | None = None,
        source: str | None = None,
        fields: dict[str, Any] | None = None,
    ) -> Connection:
        """Create a new connection.

        Calls ``POST /users/{userId}/connections``. ``fields`` carry the
        connector-specific credential fields by ``name``; Powens expects
        them at the top level of the request body, alongside
        ``id_connector``/``connector_uuid``.
        """
        if id_connector is None and connector_uuid is None:
            raise ValueError("id_connector or connector_uuid is required")
        body: dict[str, Any] = {}
        if id_connector is not None:
            body["id_connector"] = id_connector
        if connector_uuid is not None:
            body["connector_uuid"] = connector_uuid
        if source is not None:
            body["source"] = source
        if fields:
            body.update(fields)
        payload = await self._http.request_json(
            "POST",
            f"/users/{user_id}/connections",
            json_body=body,
        )
        return self._parse(Connection, payload)

    async def list_all(
        self,
        *,
        user_id: int | str = "me",
        expand: str | None = None,
    ) -> ConnectionsList:
        """Fetch all connections in a single call (no pagination).

        Calls ``GET /users/{userId}/connections``. Prefer :meth:`list`
        for lazy iteration; this helper is occasionally convenient when
        the set is small.
        """
        params: dict[str, Any] = {}
        if expand is not None:
            params["expand"] = expand
        payload = await self._http.request_json(
            "GET",
            f"/users/{user_id}/connections",
            params=params,
        )
        return self._parse(ConnectionsList, payload)

    def list(
        self,
        *,
        user_id: int | str = "me",
        expand: str | None = None,
        limit: int | None = None,
        include_all: bool = False,
    ) -> AsyncOffsetPageIterator[Connection]:
        """List the user's connections (lazy).

        Calls ``GET /users/{userId}/connections``.
        """
        params: dict[str, Any] = {}
        if expand is not None:
            params["expand"] = expand
        if include_all:
            params["all"] = ""
        return AsyncOffsetPageIterator[Connection](
            http=self._http,
            path=f"/users/{user_id}/connections",
            model=Connection,
            params=params,
            items_key="connections",
            limit=limit,
        )

    async def get(
        self,
        *,
        connection_id: int,
        user_id: int | str = "me",
        expand: str | None = None,
    ) -> Connection:
        """Get a single connection.

        Calls ``GET /users/{userId}/connections/{connectionId}``.
        """
        params: dict[str, Any] | None = None
        if expand is not None:
            params = {"expand": expand}
        payload = await self._http.request_json(
            "GET",
            f"/users/{user_id}/connections/{connection_id}",
            params=params,
        )
        return self._parse(Connection, payload)

    async def update(
        self,
        *,
        connection_id: int,
        user_id: int | str = "me",
        source: str | None = None,
        active: bool | None = None,
        expire: str | None = None,
        resume: bool | None = None,
        refresh_auth: bool | None = None,
        fields: dict[str, Any] | None = None,
        background: bool = False,
    ) -> Connection:
        """Update a connection — supports OTP/additional-info submission.

        Calls ``POST /users/{userId}/connections/{connectionId}``. The
        ``fields`` mapping carries connector-field values keyed by their
        ``name`` (this is how the OTP flow is implemented: pass the OTP
        value under the connector's field name, together with any other
        required fields).
        """
        body: dict[str, Any] = {}
        if source is not None:
            body["source"] = source
        if active is not None:
            body["active"] = active
        if expire is not None:
            body["expire"] = expire
        if resume is not None:
            body["resume"] = resume
        if refresh_auth is not None:
            body["refresh_auth"] = refresh_auth
        if fields:
            body.update(fields)
        params: dict[str, Any] | None = {"background": "true"} if background else None
        payload = await self._http.request_json(
            "POST",
            f"/users/{user_id}/connections/{connection_id}",
            params=params,
            json_body=body,
        )
        return self._parse(Connection, payload)

    async def sync(
        self,
        *,
        connection_id: int,
        user_id: int | str = "me",
        psu_requested: bool = True,
    ) -> Connection:
        """Trigger a synchronization of a connection.

        Calls ``PUT /users/{userId}/connections/{connectionId}``.
        ``psu_requested=True`` (default) matches the documented default;
        set it to ``False`` for non-PSU-driven refreshes.
        """
        params = {"psu_requested": "true" if psu_requested else "false"}
        payload = await self._http.request_json(
            "PUT",
            f"/users/{user_id}/connections/{connection_id}",
            params=params,
        )
        return self._parse(Connection, payload)

    async def delete(
        self,
        *,
        connection_id: int,
        user_id: int | str = "me",
    ) -> None:
        """Delete a connection (GDPR-compliant hard delete).

        Calls ``DELETE /users/{userId}/connections/{connectionId}``.
        Returns ``None`` (204 No Content).
        """
        await self._http.request_json(
            "DELETE",
            f"/users/{user_id}/connections/{connection_id}",
        )

    async def force_sync(
        self,
        *,
        connection_id: int,
        user_id: int | str = "me",
        psu_requested: bool = True,
    ) -> Connection:
        """Alias of :meth:`sync` for source compatibility."""
        return await self.sync(
            connection_id=connection_id,
            user_id=user_id,
            psu_requested=psu_requested,
        )

    # ------------------------------------------------------------------
    # Web authorization (separate from webview)
    # ------------------------------------------------------------------

    async def webauth_url(
        self,
        *,
        client_id: int,
        redirect_uri: str,
        id_connector: int | None = None,
        id_connection: int | None = None,
        source: str | None = None,
        state: str | None = None,
    ) -> WebauthURL:
        """Build a web-authorization URL for webauth connectors.

        Calls ``GET /webauth-url``. Requires a user token.
        """
        params: dict[str, Any] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
        }
        if id_connector is not None:
            params["id_connector"] = id_connector
        if id_connection is not None:
            params["id_connection"] = id_connection
        if source is not None:
            params["source"] = source
        if state is not None:
            params["state"] = state
        payload = await self._http.request_json("GET", "/webauth-url", params=params)
        return self._parse(WebauthURL, payload)

    # ------------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------------

    async def list_sources(
        self,
        *,
        connection_id: int,
        user_id: int | str = "me",
        include_all: bool = False,
    ) -> ConnectionSourcesList:
        """Calls ``GET /users/{u}/connections/{id}/sources``."""
        params: dict[str, Any] = {}
        if include_all:
            params["all"] = ""
        payload = await self._http.request_json(
            "GET",
            f"/users/{user_id}/connections/{connection_id}/sources",
            params=params,
        )
        return self._parse(ConnectionSourcesList, payload)

    async def get_source(
        self,
        *,
        connection_id: int,
        source_id: int,
        user_id: int | str = "me",
        include_all: bool = False,
    ) -> ConnectionSource:
        """Calls ``GET /users/{u}/connections/{id}/sources/{sid}``."""
        params: dict[str, Any] = {}
        if include_all:
            params["all"] = ""
        payload = await self._http.request_json(
            "GET",
            f"/users/{user_id}/connections/{connection_id}/sources/{source_id}",
            params=params,
        )
        return self._parse(ConnectionSource, payload)

    async def update_source(
        self,
        *,
        connection_id: int,
        source_id: int,
        user_id: int | str = "me",
        disabled: bool | None = None,
        include_all: bool = False,
    ) -> ConnectionSource:
        """Calls ``POST /users/{u}/connections/{id}/sources/{sid}``."""
        body: dict[str, Any] = {}
        if disabled is not None:
            body["disabled"] = disabled
        params: dict[str, Any] = {}
        if include_all:
            params["all"] = ""
        payload = await self._http.request_json(
            "POST",
            f"/users/{user_id}/connections/{connection_id}/sources/{source_id}",
            params=params,
            json_body=body,
        )
        return self._parse(ConnectionSource, payload)

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    async def list_logs_raw(
        self,
        *,
        connection_id: int,
        user_id: int | str = "me",
        min_date: str | None = None,
        max_date: str | None = None,
        id_source: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """Calls ``GET /users/{u}/connections/{id}/logs``.

        The Powens documentation does not formalize the log item shape.
        The SDK returns the raw JSON payload here so callers can inspect
        it; a typed model will be added once the shape stabilizes in the
        reference.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if min_date is not None:
            params["min_date"] = min_date
        if max_date is not None:
            params["max_date"] = max_date
        if id_source is not None:
            params["id_source"] = id_source
        return await self._http.request_json(
            "GET",
            f"/users/{user_id}/connections/{connection_id}/logs",
            params=params,
        )


__all__ = ["ConnectionsResource"]
