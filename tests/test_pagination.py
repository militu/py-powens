"""Tests for both paginators: offset-based and relational (cursor)."""

from __future__ import annotations

import httpx
import pytest
import respx

from powens import PowensClient, PowensSerializationError
from powens.models import Page, PaginationLinks
from powens.models.user import User
from powens.resources.pagination import AsyncCursorPageIterator

# ---------------------------------------------------------------------------
# Offset paginator
# ---------------------------------------------------------------------------


def _conn(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "id": 1,
        "id_connector": 10,
        "connector_uuid": "u",
        "active": True,
        "state": None,
    }
    body.update(overrides)
    return body


@respx.mock
async def test_offset_walks_multiple_pages(client: PowensClient, base_url: str) -> None:
    def _page(items: list[dict[str, object]]) -> httpx.Response:
        return httpx.Response(200, json={"connections": items, "total": 5})

    route = respx.get(f"{base_url}/users/me/connections").mock(
        side_effect=[
            _page([_conn(id=i) for i in range(1, 3)]),
            _page([_conn(id=i) for i in range(3, 5)]),
            _page([_conn(id=5)]),
        ]
    )
    collected = [c async for c in client.connections.list(limit=2)]
    assert [c.id for c in collected] == [1, 2, 3, 4, 5]
    assert route.call_count == 3


@respx.mock
async def test_offset_by_page_yields_one_page_per_round_trip(
    client: PowensClient, base_url: str
) -> None:
    respx.get(f"{base_url}/users/me/connections").mock(
        side_effect=[
            httpx.Response(
                200,
                json={"connections": [_conn(id=1), _conn(id=2)], "total": 3},
            ),
            httpx.Response(200, json={"connections": [_conn(id=3)], "total": 3}),
        ]
    )
    pages = []
    async for page in client.connections.list(limit=2).by_page():
        pages.append([c.id for c in page.items])
    assert pages == [[1, 2], [3]]


@respx.mock
async def test_offset_stops_on_empty_page(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/connections").mock(
        return_value=httpx.Response(200, json={"connections": [], "total": 0}),
    )
    collected = [c async for c in client.connections.list()]
    assert collected == []
    assert route.call_count == 1


@respx.mock
async def test_offset_forwards_filters(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users/me/connections").mock(
        return_value=httpx.Response(200, json={"connections": [], "total": 0}),
    )
    pages = client.connections.list(
        expand="connector",
        limit=50,
    )
    async for _ in pages.by_page():
        break
    sent = route.calls.last.request
    assert "expand=connector" in str(sent.url)
    assert "limit=50" in str(sent.url)


@respx.mock
async def test_permissive_parsing_ignores_unknown_fields(
    client: PowensClient, base_url: str
) -> None:
    respx.get(f"{base_url}/users/me/connections").mock(
        return_value=httpx.Response(
            200,
            json={
                "connections": [
                    {
                        "id": 1,
                        "id_connector": 10,
                        "connector_uuid": "u",
                        "active": True,
                        "state": None,
                        "some_future_field": {"x": 1},
                        "another_one": [1, 2, 3],
                    }
                ],
                "total": 1,
            },
        )
    )
    items = [c async for c in client.connections.list()]
    assert items[0].id == 1


@respx.mock
async def test_malformed_item_raises_serialization_error(
    client: PowensClient, base_url: str
) -> None:
    respx.get(f"{base_url}/users/me/connections").mock(
        return_value=httpx.Response(
            200,
            json={"connections": [{"id": "not-an-int"}], "total": 1},
        )
    )
    with pytest.raises(PowensSerializationError):
        async for _ in client.connections.list():
            break


# ---------------------------------------------------------------------------
# Cursor (relational) paginator
# ---------------------------------------------------------------------------


@respx.mock
async def test_cursor_follows_links_next_href(client: PowensClient, base_url: str) -> None:
    # Initial call returns a payload with _links.next pointing to an
    # absolute URL. The cursor paginator must follow it verbatim (Powens
    # docs: "opaque, absolute").
    next_url = f"{base_url}/users?cursor=abc123"
    respx.get(f"{base_url}/users", params={"limit": 2}).mock(
        return_value=httpx.Response(
            200,
            json={
                "users": [{"id": 1}, {"id": 2}],
                "_links": {
                    "self": {"href": f"{base_url}/users?limit=2"},
                    "prev": None,
                    "next": {"href": next_url},
                },
            },
        )
    )
    respx.get(next_url).mock(
        return_value=httpx.Response(
            200,
            json={
                "users": [{"id": 3}],
                "_links": {
                    "self": {"href": next_url},
                    "prev": None,
                    "next": None,
                },
            },
        )
    )
    iterator = AsyncCursorPageIterator[User](
        http=client._http,
        path="/users",
        model=User,
        items_key="users",
        limit=2,
    )
    collected = [u.id async for u in iterator]
    assert collected == [1, 2, 3]


@respx.mock
async def test_cursor_refuses_cross_origin_next(client: PowensClient, base_url: str) -> None:
    respx.get(f"{base_url}/users", params={"limit": 2}).mock(
        return_value=httpx.Response(
            200,
            json={
                "users": [{"id": 1}],
                "_links": {
                    "self": {"href": f"{base_url}/users"},
                    "next": {"href": "https://evil.example.com/steal?token=1"},
                    "prev": None,
                },
            },
        )
    )
    iterator = AsyncCursorPageIterator[User](
        http=client._http,
        path="/users",
        model=User,
        items_key="users",
        limit=2,
    )
    with pytest.raises(ValueError, match="Refusing to follow cursor URL"):
        [_ async for _ in iterator]


@respx.mock
async def test_cursor_stops_when_next_is_null(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/users").mock(
        return_value=httpx.Response(
            200,
            json={
                "users": [{"id": 1}],
                "_links": {"self": None, "prev": None, "next": None},
            },
        )
    )
    iterator = AsyncCursorPageIterator[User](
        http=client._http,
        path="/users",
        model=User,
        items_key="users",
        limit=50,
    )
    collected = [u.id async for u in iterator]
    assert collected == [1]
    assert route.call_count == 1


# ---------------------------------------------------------------------------
# Page envelope
# ---------------------------------------------------------------------------


def test_page_exposes_links_and_total() -> None:
    page: Page[User] = Page[User](
        items=[],
        total=42,
        links=PaginationLinks(
            self=None,
            prev=None,
            next=None,
        ),
    )
    assert page.total == 42
    assert page.links is not None


def test_pagination_links_all_nullable() -> None:
    links = PaginationLinks()
    assert links.self is None
    assert links.prev is None
    assert links.next is None
