"""Users resource.

Endpoints under ``/users/*`` as documented in
https://docs.powens.com/api-reference/users.

- ``GET /users`` and ``DELETE /users/{id}`` require a _users token_
  (available in the admin console). The SDK exposes them; the caller is
  responsible for providing the correct bearer token.
- ``GET /users/{id}`` accepts a user token. ``GET /users/me`` is the
  idiomatic call to retrieve the authenticated user.
"""

from __future__ import annotations

from powens.models.user import User, UsersList
from powens.resources._base import Resource


class UsersResource(Resource):
    """Endpoints under ``/users/*``."""

    async def list_all(self) -> UsersList:
        """List all users of the domain.

        Calls ``GET /users`` — requires a *users token* (admin console).
        """
        payload = await self._http.request_json("GET", "/users")
        return self._parse(UsersList, payload)

    async def get(self, *, user_id: int | str = "me") -> User:
        """Get a single user by ID (``"me"`` for the authenticated user).

        Calls ``GET /users/{userId}``.
        """
        payload = await self._http.request_json("GET", f"/users/{user_id}")
        return self._parse(User, payload)

    async def me(self) -> User:
        """Convenience shortcut for ``GET /users/me``."""
        return await self.get(user_id="me")

    async def delete(self, *, user_id: int | str = "me") -> None:
        """Delete a user by ID.

        Calls ``DELETE /users/{userId}``. Returns ``None`` (204 No Content).
        """
        await self._http.request_json("DELETE", f"/users/{user_id}")


__all__ = ["UsersResource"]
