"""Pagination envelope models.

Powens documents two pagination strategies (see
https://docs.powens.com/api-reference/overview/api-design#lists-pagination):

- **Offset pagination**: most listing endpoints, controlled via ``limit``
  and ``offset`` query parameters.
- **Relational pagination**: payloads include a ``_links`` object with
  opaque URLs to the previous, current and next pages. The URLs are
  absolute and must be followed verbatim. This mode is used by
  ``/users/me/transactions`` (documented) and may be used by other
  endpoints.

``Page`` is the generic envelope exposed by the SDK to callers; the raw
Powens response keeps whatever extra keys the endpoint exposes (e.g.
``balances`` on accounts, ``result_min_date`` on transactions) — these
are not typed here because they are endpoint-specific.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import Field

from powens.models.base import PowensModel

T = TypeVar("T")


class Link(PowensModel):
    """A single link object inside a :class:`PaginationLinks` envelope."""

    href: str


class PaginationLinks(PowensModel):
    """Relational pagination links as documented by Powens.

    All three fields can be ``None`` (e.g. ``prev`` is ``None`` on the
    first page, ``next`` is ``None`` on the last page).
    """

    self: Link | None = None
    prev: Link | None = None
    next: Link | None = None


class Page(PowensModel, Generic[T]):
    """Generic SDK-side page envelope.

    - ``items``: parsed items from the current page.
    - ``total``: when the endpoint exposes a ``total`` key (offset mode).
    - ``links``: populated from the endpoint's ``_links`` key when
      relational pagination is used; ``None`` for pure-offset endpoints.
    """

    items: list[T] = Field(default_factory=list)
    total: int | None = None
    links: PaginationLinks | None = None


__all__ = ["Link", "Page", "PaginationLinks"]
