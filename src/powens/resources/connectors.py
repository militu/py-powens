"""Connectors resource.

Mirrors https://docs.powens.com/api-reference/connectors. GET endpoints
do not require authentication; PUT / PATCH endpoints require a *config
token* (admin console) and are exposed here as plain methods — the
caller is responsible for providing the correct bearer token.
"""

from __future__ import annotations

from typing import Any

from powens.models.connector import (
    Connector,
    ConnectorsList,
    ConnectorSource,
    ConnectorSourcesList,
)
from powens.resources._base import Resource


class ConnectorsResource(Resource):
    """Endpoints under ``/connectors/*``."""

    async def list(
        self,
        *,
        country_codes: str | None = None,
        id_payment: str | None = None,
    ) -> ConnectorsList:
        """List all connectors available on the domain.

        Calls ``GET /connectors``. No authentication required.
        """
        params: dict[str, Any] = {}
        if country_codes is not None:
            params["country_codes"] = country_codes
        if id_payment is not None:
            params["id_payment"] = id_payment
        payload = await self._http.request_json(
            "GET",
            "/connectors",
            params=params,
            auth_required=False,
        )
        return self._parse(ConnectorsList, payload)

    async def get(
        self,
        *,
        connector_uuid: str | int,
        expand: str | None = None,
    ) -> Connector:
        """Get a single connector by UUID (integer IDs are also accepted).

        Calls ``GET /connectors/{connectorUuid}``.
        """
        params: dict[str, Any] = {}
        if expand is not None:
            params["expand"] = expand
        payload = await self._http.request_json(
            "GET",
            f"/connectors/{connector_uuid}",
            params=params,
            auth_required=False,
        )
        return self._parse(Connector, payload)

    async def update(
        self,
        *,
        connector_uuid: str | int,
        body: dict[str, Any],
    ) -> Connector:
        """Update a single connector.

        Calls ``PUT /connectors/{connectorUuid}``. Requires a *config
        token* provided via the client's bearer header.
        """
        payload = await self._http.request_json(
            "PUT",
            f"/connectors/{connector_uuid}",
            json_body=body,
        )
        return self._parse(Connector, payload)

    async def batch_update(self, body: dict[str, dict[str, Any]]) -> None:
        """Batch enable/disable connectors.

        Calls ``PATCH /connectors``. Body is a mapping from connector
        UUID to :class:`ConnectorUpdateRequest`-shaped dicts. Requires a
        *config token*.
        """
        await self._http.request_json("PATCH", "/connectors", json_body=body)

    # -- Sources ------------------------------------------------------

    async def list_sources(
        self,
        *,
        connector_uuid: str | int,
        country_codes: str | None = None,
    ) -> ConnectorSourcesList:
        """List the sources for a connector.

        Calls ``GET /connectors/{connectorUuid}/sources``. No auth.
        """
        params: dict[str, Any] = {}
        if country_codes is not None:
            params["country_codes"] = country_codes
        payload = await self._http.request_json(
            "GET",
            f"/connectors/{connector_uuid}/sources",
            params=params,
            auth_required=False,
        )
        return self._parse(ConnectorSourcesList, payload)

    async def get_source(
        self,
        *,
        connector_uuid: str | int,
        source_id: int,
    ) -> ConnectorSource:
        """Get a single source of a connector.

        Calls ``GET /connectors/{connectorUuid}/sources/{sourceId}``.
        """
        payload = await self._http.request_json(
            "GET",
            f"/connectors/{connector_uuid}/sources/{source_id}",
            auth_required=False,
        )
        return self._parse(ConnectorSource, payload)

    async def update_source(
        self,
        *,
        connector_uuid: str | int,
        source_id: int,
        body: dict[str, Any],
    ) -> ConnectorSource:
        """Update a source of a connector.

        Calls ``PUT /connectors/{connectorUuid}/sources/{sourceId}``.
        Requires a *config token*.
        """
        payload = await self._http.request_json(
            "PUT",
            f"/connectors/{connector_uuid}/sources/{source_id}",
            json_body=body,
        )
        return self._parse(ConnectorSource, payload)


__all__ = ["ConnectorsResource"]
