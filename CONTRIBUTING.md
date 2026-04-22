# Contributing to py-powens

Thanks for your interest. This is an unofficial, community-maintained SDK.

## Dev setup

```bash
mise install      # Python 3.13 + uv
uv sync           # install all deps (including dev)
make pre-commit-install
```

## Quality gate

`make check` must pass locally before pushing:

- `ruff check .`
- `ruff format --check .`
- `mypy .` (strict mode)
- `pytest -q`

## PRs

- Target `main`. Small, focused PRs.
- Every change that affects public API must include a test.
- Update `CHANGELOG.md` under `[Unreleased]`.
- Conventional Commits style is appreciated: `feat:`, `fix:`, `docs:`,
  `test:`, `chore:`, `refactor:`.

## Adding / updating models

Models mirror the
[public Powens API reference](https://docs.powens.com/api-reference/)
1:1. When Powens updates a field, update the matching Pydantic model **and**
the test fixture. Models are `frozen=True` with `extra="ignore"` — do not
switch to `extra="forbid"`.

## Security

Security-sensitive reports go through [SECURITY.md](./SECURITY.md), not
GitHub issues.
