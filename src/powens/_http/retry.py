"""Light retry policy for the internal HTTP client.

We only retry on transient conditions:
- network errors (``httpx.TransportError``)
- HTTP 502, 503, 504
- HTTP 429 (respecting ``Retry-After`` when provided)

``GET`` requests are retried by default. Non-idempotent verbs require an
explicit opt-in via ``retry_non_idempotent=True``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Declarative retry policy used by :class:`HTTPClient`.

    Attributes:
        max_attempts: Total number of attempts, including the initial one.
            ``1`` disables retries.
        base_delay: Base delay in seconds for exponential backoff.
        max_delay: Upper bound for the per-attempt delay, in seconds.
        jitter: Maximum random jitter added to each delay, in seconds.
        retry_non_idempotent: When ``True``, also retry non-idempotent verbs
            (POST/PATCH/DELETE). Off by default to stay safe.
    """

    max_attempts: int = 3
    base_delay: float = 0.25
    max_delay: float = 5.0
    jitter: float = 0.1
    retry_non_idempotent: bool = False

    def compute_delay(self, attempt: int, retry_after: float | None = None) -> float:
        """Return the delay (in seconds) before attempt number ``attempt``.

        ``attempt`` is 1-indexed; ``compute_delay(1, ...)`` is the delay
        before the first *retry* (i.e. second try).
        """
        if retry_after is not None and retry_after >= 0:
            return min(retry_after, self.max_delay)
        backoff: float = self.base_delay * float(2 ** max(attempt - 1, 0))
        backoff = min(backoff, self.max_delay)
        if self.jitter > 0:
            backoff += random.uniform(0, self.jitter)
        return backoff


RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 502, 503, 504})
IDEMPOTENT_METHODS: frozenset[str] = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


__all__ = ["IDEMPOTENT_METHODS", "RETRYABLE_STATUS_CODES", "RetryPolicy"]
