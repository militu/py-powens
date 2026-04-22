"""User data model.

Mirrors https://docs.powens.com/api-reference/users.
"""

from __future__ import annotations

from datetime import datetime

from powens.models.base import PowensModel


class User(PowensModel):
    """A Powens user.

    Fields per the documented schema: ``id`` (integer) and ``signin``
    (datetime). Additional fields may appear on webhooks payloads but the
    documented data model only exposes these two.
    """

    id: int
    signin: datetime | None = None


class UsersList(PowensModel):
    """Envelope returned by ``GET /users``."""

    users: list[User]


__all__ = ["User", "UsersList"]
