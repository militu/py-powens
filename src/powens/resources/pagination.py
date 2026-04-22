"""Async lazy paginators for Powens listing endpoints.

Two iterators are exposed:

- :class:`AsyncOffsetPageIterator` — offset/limit pagination (the
  majority of endpoints).
- :class:`AsyncCursorPageIterator` — relational pagination via the
  ``_links.next.href`` URL exposed by Powens on endpoints such as
  ``/users/me/transactions``.

Both are single-use: re-iterating requires a fresh instance (offset is
advanced in-place, cursor state is consumed).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any

from pydantic import ValidationError

from powens._http.client import HTTPClient
from powens.exceptions import PowensSerializationError
from powens.models.base import PowensModel
from powens.models.pagination import Link, Page, PaginationLinks


class AsyncOffsetPageIterator[T: PowensModel]:
    """Lazy iterator for offset-based Powens listings.

    Supports two iteration modes:

    - ``async for item in iterator: ...`` — yields individual items.
    - ``async for page in iterator.by_page(): ...`` — yields one
      :class:`Page` per round-trip.

    Iteration stops when a page contains fewer items than the requested
    ``limit`` or when the returned list is empty. The iterator is
    **single-use**; calling :meth:`by_page` twice is a no-op after the
    first consumption.
    """

    DEFAULT_LIMIT: int = 100

    def __init__(
        self,
        *,
        http: HTTPClient,
        path: str,
        model: type[T],
        params: Mapping[str, Any] | None = None,
        items_key: str = "",
        limit: int | None = None,
    ) -> None:
        self._http = http
        self._path = path
        self._model = model
        self._items_key = items_key
        self._params: dict[str, Any] = dict(params or {})
        if limit is not None:
            self._params["limit"] = limit
        self._params.setdefault("limit", self.DEFAULT_LIMIT)
        self._params.setdefault("offset", 0)
        self._exhausted: bool = False

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iter_items()

    async def _iter_items(self) -> AsyncIterator[T]:
        async for page in self.by_page():
            for item in page.items:
                yield item

    async def by_page(self) -> AsyncIterator[Page[T]]:
        """Yield pages one at a time, following the offset."""
        if self._exhausted:
            return
        offset: int = int(self._params.get("offset", 0))
        limit: int = int(self._params.get("limit", self.DEFAULT_LIMIT))
        while True:
            params = dict(self._params)
            params["offset"] = offset
            params["limit"] = limit
            payload = await self._http.request_json("GET", self._path, params=params)
            page = _build_page(payload, self._model, self._items_key)
            yield page

            if not page.items or len(page.items) < limit:
                break
            offset += len(page.items)
        self._exhausted = True


class AsyncCursorPageIterator[T: PowensModel]:
    """Lazy iterator for Powens relational pagination.

    Works by issuing the first request with the caller-provided
    parameters, then following ``_links.next.href`` (an absolute URL
    returned by Powens) until ``next`` is ``None``. The cursor URLs are
    opaque and forwarded as-is, as required by the documentation.

    Supports both ``async for item`` and ``async for page in .by_page()``.
    """

    DEFAULT_LIMIT: int = 100

    def __init__(
        self,
        *,
        http: HTTPClient,
        path: str,
        model: type[T],
        params: Mapping[str, Any] | None = None,
        items_key: str = "",
        limit: int | None = None,
    ) -> None:
        self._http = http
        self._path = path
        self._model = model
        self._items_key = items_key
        self._initial_params: dict[str, Any] = dict(params or {})
        if limit is not None:
            self._initial_params["limit"] = limit
        self._initial_params.setdefault("limit", self.DEFAULT_LIMIT)
        self._exhausted: bool = False

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iter_items()

    async def _iter_items(self) -> AsyncIterator[T]:
        async for page in self.by_page():
            for item in page.items:
                yield item

    async def by_page(self) -> AsyncIterator[Page[T]]:
        """Yield pages one at a time, following ``_links.next.href``."""
        if self._exhausted:
            return
        # First request uses the caller-provided params + path.
        payload = await self._http.request_json("GET", self._path, params=self._initial_params)
        while True:
            page = _build_page(payload, self._model, self._items_key)
            yield page
            next_href = _next_href(page.links)
            if next_href is None:
                break
            payload = await self._http.get_absolute_url(next_href)
        self._exhausted = True


def _next_href(links: PaginationLinks | None) -> str | None:
    if links is None or links.next is None:
        return None
    return links.next.href


def _build_page[T: PowensModel](payload: Any, model: type[T], items_key: str) -> Page[T]:
    raw_items, total, raw_links = _extract_envelope(payload, items_key)
    parsed: list[T] = []
    for raw in raw_items:
        try:
            parsed.append(model.model_validate(raw))
        except ValidationError as exc:
            raise PowensSerializationError(
                f"Failed to parse a {model.__name__} item: {exc}"
            ) from exc
    links = _build_links(raw_links)
    return Page[T](items=parsed, total=total, links=links)


def _extract_envelope(payload: Any, items_key: str) -> tuple[list[Any], int | None, Any]:
    if isinstance(payload, list):
        return list(payload), None, None
    if not isinstance(payload, dict):
        raise PowensSerializationError(
            f"Unexpected Powens listing payload (not a list or object): {type(payload).__name__}"
        )

    total_val = payload.get("total")
    total: int | None = (
        int(total_val) if isinstance(total_val, int) and not isinstance(total_val, bool) else None
    )
    raw_links = payload.get("_links")

    if items_key and items_key in payload:
        items = payload[items_key]
        if not isinstance(items, list):
            raise PowensSerializationError(
                f"Expected list under key {items_key!r}, got {type(items).__name__}"
            )
        return list(items), total, raw_links

    # Fallback: first list value in the object.
    for value in payload.values():
        if isinstance(value, list):
            return list(value), total, raw_links

    raise PowensSerializationError("Powens listing payload did not contain any list of items")


def _build_links(raw: Any) -> PaginationLinks | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return None

    def _link(value: Any) -> Link | None:
        if value is None:
            return None
        if isinstance(value, dict) and isinstance(value.get("href"), str):
            return Link(href=value["href"])
        return None

    return PaginationLinks(
        self=_link(raw.get("self")),
        prev=_link(raw.get("prev")),
        next=_link(raw.get("next")),
    )


__all__ = ["AsyncCursorPageIterator", "AsyncOffsetPageIterator"]
