# py-powens

[![PyPI version](https://img.shields.io/pypi/v/py-powens.svg)](https://pypi.org/project/py-powens/)
[![Python versions](https://img.shields.io/pypi/pyversions/py-powens.svg)](https://pypi.org/project/py-powens/)
[![CI](https://github.com/militu/py-powens/actions/workflows/ci.yml/badge.svg)](https://github.com/militu/py-powens/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **Unofficial, third-party SDK.** Not affiliated with or endorsed by
> Powens. "Powens" is used here only to describe compatibility with the
> Powens API. Users of this SDK are bound by
> [Powens' own Terms of Service](https://www.powens.com/powens-terms-and-conditions-of-use/).

## Status

**Alpha (0.x)** — the public surface may still change in minor versions
until `1.0`. Pin strictly (`py-powens==0.1.*`) for reproducibility.
Semantic versioning applies from `1.0.0` onwards.

A modern, typed, async-only Python SDK for the
[Powens](https://www.powens.com/) banking API, built 1:1 from the
[public API reference](https://docs.powens.com/api-reference/).

- **Python 3.13+**, fully typed, `py.typed`.
- **Async-only** on top of `httpx`.
- **Immutable Pydantic v2 models**, permissive on unknown fields.
- **Both paginations** supported: offset (most endpoints) and relational
  cursor (`_links.next.href`, used by transactions).
- **Typed exception hierarchy** that parses the Powens error envelope
  `{ code, description, message, request_id }`.
- **Light retry** on transient errors + **injectable circuit breaker**.
- **Composition over inheritance** — inject an `httpx.AsyncClient` or a
  test transport for full control.

The SDK speaks to the Powens API and nothing else: no DB, no cache, no
scheduler, no cross-provider abstractions. Anything beyond "talk to the
Powens API" is the caller's job.

---

## Installation

```bash
uv add py-powens      # recommended
pip install py-powens
poetry add py-powens
```

Requires **Python 3.13+**. Runtime dependencies: `httpx` and `pydantic` (v2).

## 30-second example

```python
import asyncio
from powens import PowensClient

async def main() -> None:
    async with PowensClient(
        base_url="https://demo.biapi.pro/2.0",
        access_token="<USER_TOKEN>",
    ) as client:
        # Iterate accounts lazily (offset pagination under the hood)
        async for account in client.accounts.list():
            print(account.id, account.name, account.balance)

asyncio.run(main())
```

Prefer the envelope (with aggregated `balances` per currency) in a single
call? Use `list_all()`:

```python
envelope = await client.accounts.list_all()
for account in envelope.accounts:
    print(account.id, account.name, account.balance)
print("EUR total:", envelope.balances and envelope.balances.get("EUR"))
```

## Quickstart

```python
import asyncio
from powens import PowensClient

async def main() -> None:
    async with PowensClient(
        base_url="https://your-domain.biapi.pro/2.0",
        access_token="<USER_TOKEN>",
    ) as client:
        # Offset-paginated listing
        async for conn in client.connections.list():
            print(conn.id, conn.state)

        # Cursor-paginated listing (transactions)
        async for tx in client.transactions.list(limit=500):
            print(tx.id, tx.value, tx.wording)

asyncio.run(main())
```

## Authentication

The SDK exposes **every** documented auth endpoint:

```python
# Create a new end-user
token = await c.auth.init_user(client_id="...", client_secret="...")
c.set_access_token(token.auth_token)

# Generate a temporary webview code
code = await c.auth.generate_code(type_="singleAccess")

# Exchange a code for a permanent token
permanent = await c.auth.exchange_code(
    code=code.code, client_id="...", client_secret="...",
)

# Renew a token (for a known user)
new = await c.auth.renew_token(
    client_id="...", client_secret="...", id_user=42,
)

# Revoke the current permanent token
await c.auth.revoke_token()

# Issue a service token (Pay product)
svc = await c.auth.generate_service_token(
    client_id="...", client_secret="...",
    scope="payments:admin",
)
```

## Webview

The Powens webview is served from a **separate host**
(`https://webview.powens.com/{lang}/{flow}`). The SDK exposes URL
builders — no HTTP call is issued:

```python
url = client.webview.connect_url(
    client_id="...",
    redirect_uri="https://your-app/cb",
    lang="fr",
    connector_capabilities=["bank"],
).url
```

Four flows are supported: `connect`, `reconnect`, `manage`, `payment`.

For the separate `/webauth-url` API endpoint (not the webview), use
`client.connections.webauth_url(...)`.

## Resources

| Resource | Coverage |
|---|---|
| `client.auth` | `init_user`, `generate_code`, `exchange_code`, `revoke_token`, `renew_token`, `generate_service_token` |
| `client.users` | `me`, `get(id)`, `list_all`, `delete` |
| `client.connectors` | `list`, `get`, `update`, `batch_update`, `list_sources`, `get_source`, `update_source` |
| `client.connections` | `create`, `list`, `list_all`, `get`, `update` (incl. OTP via fields), `sync`, `delete`, `list_sources`, `get_source`, `update_source`, `webauth_url`, `list_logs_raw` |
| `client.accounts` | `list`, `list_all` (envelope with `balances`/`coming_balances`), `get`, `update` |
| `client.account_types` | `list`, `get` |
| `client.currencies` | `list` |
| `client.transactions` | `list` (cursor), `list_page`, `get`, `update` |
| `client.investments` | `list`, `list_all` (portfolio aggregates), `get`, `history` |
| `client.market_orders` | `list`, `get` |
| `client.pockets` | `list`, `get` |
| `client.loan_amortizations` | `list` |
| `client.balances` | `get` |
| `client.account_ownerships` | `list` (feature-gated) |
| `client.indicators` | `get` |
| `client.webview` | `connect_url`, `reconnect_url`, `manage_url`, `payment_url` |

## Pagination

```python
# Offset (connections, accounts, investments, market orders, …)
async for c in client.connections.list():
    ...

async for page in client.connections.list(limit=50).by_page():
    print(page.total, [c.id for c in page.items])

# Relational cursor (transactions)
async for tx in client.transactions.list(limit=1000):
    ...

# Single-page call that exposes the envelope dates
env = await client.transactions.list_page(
    account_id=1, min_date=date(2024, 1, 1),
)
print(env.first_date, env.last_date)
```

## Error handling

The SDK parses the common Powens error envelope and exposes a typed
hierarchy. Powens explicitly recommends branching on `error_code` over
HTTP status — so `PowensHTTPError.error_code` is a first-class attribute.

```
PowensError
├── PowensHTTPError            # base (has .error_code, .error_description, ...)
│   ├── PowensBadRequestError        # 400
│   ├── PowensAuthError              # 401 / 403
│   ├── PowensNotFoundError          # 404
│   ├── PowensConflictError          # 409
│   ├── PowensRateLimitError         # 429 (has .retry_after)
│   ├── PowensServerError            # 500
│   └── PowensServiceUnavailableError# 503
├── PowensConnectionError      # network failure
├── PowensSerializationError   # response shape mismatch
└── PowensCircuitOpenError     # injected breaker short-circuited
```

```python
from powens import PowensErrorCode, PowensHTTPError

try:
    await client.accounts.get(account_id=999)
except PowensHTTPError as err:
    if err.error_code == PowensErrorCode.WRONG_PASS.value:
        ...
```

## Retry + circuit breaker

Transient retries apply to network errors, 429, 502, 503, 504 — never
500 (a 500 on a finance API is ambiguous; silently retrying write
requests risks double-effects). Only idempotent verbs
(GET/HEAD/OPTIONS/PUT/DELETE) are retried by default.

```python
from powens import PowensClient, RetryPolicy

policy = RetryPolicy(max_attempts=5, base_delay=0.5, max_delay=5.0)
async with PowensClient(base_url=..., retry_policy=policy) as c:
    ...
```

A `NoOpCircuitBreaker` ships by default. Inject your own implementation
(conforming to the `CircuitBreaker` protocol) to integrate with an
observability / control plane.

## Development

```bash
mise install
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
```

Tests use `respx` and do not need network access.

## Fidelity

This SDK mirrors the [public Powens API reference](https://docs.powens.com/api-reference/)
1:1 — every documented field appears on the corresponding Pydantic
model, including deprecated fields (marked in code). Enums list the
documented values but tolerate unknown strings, as the reference
requires.

## Known limitations

- Async-only; no sync wrapper. Use `asyncio.run(...)` in scripts or
  integrate inside an existing event loop.
- `client.indicators` and `client.account_ownerships` depend on
  feature-gated Powens endpoints — your domain must have them enabled.
- Webhooks are **not** covered (they are a server-side concern, not an
  API-client one).
- The SDK does not persist tokens; token refresh and storage are the
  caller's responsibility.

## Support

This is a community-maintained SDK. For bugs and feature requests, use
[GitHub Issues](https://github.com/militu/py-powens/issues). For
questions about the Powens API itself, refer to the
[official documentation](https://docs.powens.com/).

## License

MIT — see [`LICENSE`](LICENSE).
