"""Shared fixtures for py-powens tests."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from powens import PowensClient, RetryPolicy

BASE_URL = "https://test.powens.local/2.0"


@pytest_asyncio.fixture
async def client() -> AsyncIterator[PowensClient]:
    """Yields a PowensClient configured with near-zero retry delays."""
    retry = RetryPolicy(max_attempts=3, base_delay=0.0, max_delay=0.0, jitter=0.0)
    async with PowensClient(
        base_url=BASE_URL,
        access_token="test-token",
        retry_policy=retry,
    ) as c:
        yield c


@pytest_asyncio.fixture
async def client_no_retry() -> AsyncIterator[PowensClient]:
    """PowensClient that never retries — useful for asserting a single call path."""
    retry = RetryPolicy(max_attempts=1)
    async with PowensClient(
        base_url=BASE_URL,
        access_token="test-token",
        retry_policy=retry,
    ) as c:
        yield c


@pytest.fixture
def base_url() -> str:
    return BASE_URL


def bank_account_payload(**overrides: object) -> dict[str, object]:
    """Return a minimal-but-conformant BankAccount payload for tests.

    ``type`` is a string here (not an object) because live Powens
    payloads return a string code, even though the public reference
    claims an ``AccountType`` object. The SDK mirrors the live reality.
    """
    body: dict[str, object] = {
        "id": 1,
        "id_connection": 1,
        "original_name": "Checking",
        "display": True,
        "type": "checking",
        "id_type": 1,
        "bookmarked": 0,
        "name": "Checking",
    }
    body.update(overrides)
    return body
