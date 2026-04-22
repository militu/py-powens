"""Auth resource.

Wraps the user and service token endpoints documented under
``/auth/*``. All bodies are sent as JSON ``application/json``.

See https://docs.powens.com/api-reference/overview/authentication for the
canonical reference.
"""

from __future__ import annotations

from powens.models.auth import (
    AuthCode,
    AuthScope,
    AuthServiceToken,
    AuthToken,
    AuthTokenExchange,
)
from powens.resources._base import Resource


class AuthResource(Resource):
    """Endpoints under ``/auth/*``."""

    # ------------------------------------------------------------------
    # User tokens
    # ------------------------------------------------------------------

    async def init_user(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> AuthToken:
        """Create a new user and return the associated access token.

        Calls ``POST /auth/init``. When both ``client_id`` and
        ``client_secret`` are supplied, the resulting token is permanent;
        otherwise it is temporary and expires in 30 minutes.
        """
        body: dict[str, str] = {}
        if client_id is not None:
            body["client_id"] = client_id
        if client_secret is not None:
            body["client_secret"] = client_secret
        payload = await self._http.request_json(
            "POST",
            "/auth/init",
            json_body=body,
            auth_required=False,
        )
        return self._parse(AuthToken, payload)

    async def generate_code(self, *, type_: str | None = None) -> AuthCode:
        """Generate a temporary code for the current user.

        Calls ``GET /auth/token/code``. Requires a valid user bearer
        token. ``type_`` maps to the ``type`` query parameter
        (``singleAccess`` or ``requestAccess``); the argument is named
        ``type_`` to avoid shadowing the Python builtin.
        """
        params: dict[str, str] = {}
        if type_ is not None:
            params["type"] = type_
        payload = await self._http.request_json(
            "GET",
            "/auth/token/code",
            params=params,
        )
        return self._parse(AuthCode, payload)

    async def exchange_code(
        self,
        *,
        code: str,
        client_id: str,
        client_secret: str,
        grant_type: str = "authorization_code",
    ) -> AuthTokenExchange:
        """Exchange a temporary code for a permanent user access token.

        Calls ``POST /auth/token/access``.
        """
        payload = await self._http.request_json(
            "POST",
            "/auth/token/access",
            json_body={
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
            },
            auth_required=False,
        )
        return self._parse(AuthTokenExchange, payload)

    async def revoke_token(self) -> None:
        """Revoke the current user's permanent access token.

        Calls ``DELETE /auth/token``. The token used in the bearer header
        is the one being revoked. Returns ``None`` (204 No Content).
        """
        await self._http.request_json("DELETE", "/auth/token")

    async def renew_token(
        self,
        *,
        client_id: str,
        client_secret: str,
        id_user: int,
        revoke_previous: bool = False,
        grant_type: str = "client_credentials",
    ) -> AuthTokenExchange:
        """Generate a new access token for an existing user.

        Calls ``POST /auth/renew``.
        """
        payload = await self._http.request_json(
            "POST",
            "/auth/renew",
            json_body={
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret,
                "id_user": id_user,
                "revoke_previous": revoke_previous,
            },
            auth_required=False,
        )
        return self._parse(AuthTokenExchange, payload)

    # ------------------------------------------------------------------
    # Service tokens
    # ------------------------------------------------------------------

    async def generate_service_token(
        self,
        *,
        client_id: str,
        client_secret: str,
        scope: str | list[str] | AuthScope | list[AuthScope],
        grant_type: str = "client_credentials",
    ) -> AuthServiceToken:
        """Generate a service token with a dedicated scope.

        Calls ``POST /auth/token``. ``scope`` may be a single scope or an
        array of scopes (Powens accepts both forms).
        """
        if isinstance(scope, AuthScope):
            scope_payload: str | list[str] = scope.value
        elif isinstance(scope, list):
            scope_payload = [s.value if isinstance(s, AuthScope) else s for s in scope]
        else:
            scope_payload = scope
        payload = await self._http.request_json(
            "POST",
            "/auth/token",
            json_body={
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": scope_payload,
            },
            auth_required=False,
        )
        return self._parse(AuthServiceToken, payload)


__all__ = ["AuthResource"]
