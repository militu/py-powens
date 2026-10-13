.PHONY: help install dev lint fmt lint-fix typecheck check test coverage ci \
	audit bandit security \
	pre-commit pre-commit-install pre-commit-run \
	notebook \
	build clean release-check compatibility-check

-include local.mk

.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================

help: ## Show help
	@echo ""
	@echo "📚 py-powens — Makefile"
	@echo ""
	@echo "🔧 Install:"
	@echo "  make install           - Install production dependencies (frozen)"
	@echo "  make dev               - Install dev dependencies"
	@echo ""
	@echo "✨ Code Quality:"
	@echo "  make lint              - Ruff check"
	@echo "  make fmt               - Ruff format + auto-fix imports"
	@echo "  make lint-fix          - Ruff --fix"
	@echo "  make typecheck         - mypy --strict"
	@echo "  make check             - lint + format-check + typecheck + tests"
	@echo ""
	@echo "🧪 Tests:"
	@echo "  make test              - Run the full test suite"
	@echo "  make coverage          - Tests with HTML coverage"
	@echo ""
	@echo "🛡️  Security:"
	@echo "  make audit             - pip-audit on runtime deps"
	@echo "  make bandit            - bandit SAST scan"
	@echo "  make security          - audit + bandit"
	@echo ""
	@echo "🔒 Pre-commit:"
	@echo "  make pre-commit        - fmt + lint + typecheck + tests"
	@echo "  make pre-commit-install - Install pre-commit framework hooks"
	@echo "  make pre-commit-run    - Run pre-commit on all files"
	@echo ""
	@echo "📓 Notebook:"
	@echo "  make notebook          - Launch Jupyter Lab in notebooks/"
	@echo ""
	@echo "📦 Release:"
	@echo "  make clean             - Remove build artifacts"
	@echo "  make build             - Build wheel + sdist"
	@echo "  make release-check     - check + audit + build + twine check"
	@echo "  make ci                - What CI runs: release-check + Python 3.13 and installed wheel"
	@echo "  Publishing: a v* tag, through PyPI Trusted Publishing (release.yml); no token"
	@echo ""

# ============================================================================
# Install
# ============================================================================

install: ## Install production dependencies
	uv sync --locked --no-dev

dev: ## Install all dev dependencies
	uv sync --locked

# ============================================================================
# Code Quality
# ============================================================================

lint: ## Ruff check
	uv run --frozen ruff check .

fmt: ## Ruff format + fix imports
	uv run --frozen ruff check --select I --fix .
	uv run --frozen ruff format .

lint-fix: ## Ruff auto-fix
	uv run --frozen ruff check --fix .

typecheck: ## mypy strict
	uv run --frozen mypy .

check: ## Full quality gate
	uv run --frozen ruff check .
	uv run --frozen ruff format --check .
	uv run --frozen mypy .
	uv run --frozen pytest -q

# ============================================================================
# Tests
# ============================================================================

test: ## Run tests
	uv run --frozen pytest

coverage: ## Tests with HTML coverage
	uv run --frozen pytest --cov=powens --cov-report=html --cov-report=term
	@echo "✅ Coverage report: htmlcov/index.html"

# ============================================================================
# Security
# ============================================================================

audit: ## pip-audit on runtime deps
	uv export --locked --no-dev --no-emit-project --no-hashes --format requirements-txt > requirements.txt
	uv run --frozen pip-audit --strict -r requirements.txt
	rm -f requirements.txt

bandit: ## bandit SAST scan
	uv run --frozen bandit -r src/powens -ll

security: audit bandit ## audit + bandit

# ============================================================================
# Pre-commit
# ============================================================================

pre-commit: ## Fast pre-commit quality gate
	@$(MAKE) fmt
	@$(MAKE) lint
	@$(MAKE) typecheck
	@$(MAKE) test

pre-commit-install: ## Install pre-commit framework hooks
	uv tool run pre-commit install
	@echo "✅ Pre-commit hooks installed. Run 'make check' before push for mypy + tests."

pre-commit-run: ## Run pre-commit hooks on all files
	uv tool run pre-commit run --all-files

# ============================================================================
# Notebook
# ============================================================================

notebook: ## Launch Jupyter Lab in notebooks/
	uv run --frozen --group notebooks jupyter lab --notebook-dir=notebooks

# ============================================================================
# Release
# ============================================================================

clean: ## Remove build artifacts
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml

build: clean ## Build wheel + sdist
	uv build

release-check: check security build ## Pre-release sanity check (check + security + build + twine)
	uv run --frozen twine check dist/*

compatibility-check: ## Tests on the declared Python minimum and imports of the installed wheel
	python scripts/ci-compatibility.py

ci: dev release-check ## What CI runs: every gate, build and declared Python compatibility
	$(MAKE) --no-print-directory compatibility-check
