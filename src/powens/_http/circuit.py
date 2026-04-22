"""Minimal circuit breaker protocol.

The SDK ships a :class:`NoOpCircuitBreaker` as the default so users get
straightforward behavior out of the box, and callers can inject their own
implementation by conforming to the :class:`CircuitBreaker` protocol. We don't
ship a fully-featured breaker on purpose — production systems typically want
to integrate with their own observability and control plane (purgatory,
pybreaker, custom).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CircuitBreaker(Protocol):
    """Protocol describing the minimal surface needed by the HTTP client.

    Implementations must be safe to call from async code but the methods
    themselves are synchronous to keep the hot path cheap.
    """

    def allow_request(self) -> bool:
        """Return ``True`` if the next request should be attempted."""
        ...

    def record_success(self) -> None:
        """Register a successful call."""
        ...

    def record_failure(self) -> None:
        """Register a failed call (connection or 5xx)."""
        ...


class NoOpCircuitBreaker:
    """Default breaker: always closed. Never blocks requests."""

    def allow_request(self) -> bool:
        return True

    def record_success(self) -> None:
        return None

    def record_failure(self) -> None:
        return None


__all__ = ["CircuitBreaker", "NoOpCircuitBreaker"]
