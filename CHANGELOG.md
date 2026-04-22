# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-04-22

### Fixed
- README "30-second example" was iterating `accounts.list_all()` (which
  returns an envelope) as an async iterator. Replaced with `accounts.list()`
  and added a second snippet demonstrating the envelope form.

### Changed
- Release workflow now runs the full quality gate (ruff, format,
  mypy --strict, pytest) before building and publishing.

## [0.1.0] - 2026-04-22

### Added
- Initial public release of the unofficial Powens Python SDK.
- Async-only `PowensClient` built on `httpx.AsyncClient`.
- Full coverage of the public Powens API reference: `auth`, `users`,
  `connectors`, `connections`, `accounts`, `account_types`, `currencies`,
  `transactions`, `investments`, `market_orders`, `pockets`,
  `loan_amortizations`, `balances`, `account_ownerships`, `indicators`,
  `webview`.
- Immutable Pydantic v2 models with permissive unknown-field handling.
- Offset and relational cursor pagination (`_links.next.href`).
- Typed exception hierarchy parsing the Powens error envelope
  (`code`, `description`, `message`, `request_id`), including a
  `PowensErrorCode` enum.
- Configurable `RetryPolicy` with idempotent-only retries and a
  pluggable `CircuitBreaker` protocol.
- Full PEP 561 type information (`py.typed`).
- 96 unit tests using `respx` (no network required).

[Unreleased]: https://github.com/militu/py-powens/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/militu/py-powens/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/militu/py-powens/releases/tag/v0.1.0
