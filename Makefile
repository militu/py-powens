.PHONY: help install dev lint fmt lint-fix typecheck check test coverage \
	audit bandit security \
	pre-commit pre-commit-install pre-commit-run \
	notebook \
	build publish clean release-check

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
	@echo "  make publish           - Publish to PyPI (requires token)"
	@echo ""

# ============================================================================
# Install
# ============================================================================

install: ## Install production dependencies
	uv sync --frozen --no-dev

dev: ## Install all dev dependencies
	uv sync --frozen

# ============================================================================
# Code Quality
# ============================================================================

lint: ## Ruff check
	uv run ruff check .

fmt: ## Ruff format + fix imports
	uv run ruff check --select I --fix .
	uv run ruff format .

lint-fix: ## Ruff auto-fix
	uv run ruff check --fix .

typecheck: ## mypy strict
	uv run mypy .

check: ## Full quality gate
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .
	uv run pytest -q

# ============================================================================
# Tests
# ============================================================================

test: ## Run tests
	uv run pytest

coverage: ## Tests with HTML coverage
	uv run pytest --cov=powens --cov-report=html --cov-report=term
	@echo "✅ Coverage report: htmlcov/index.html"

# ============================================================================
# Security
# ============================================================================

audit: ## pip-audit on runtime deps
	uv export --no-dev --no-emit-project --no-hashes --format requirements-txt > requirements.txt
	uv tool run pip-audit --strict -r requirements.txt
	rm -f requirements.txt

bandit: ## bandit SAST scan
	uv tool run bandit -r src/powens -ll

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
	uv run --group notebooks jupyter lab --notebook-dir=notebooks

# ============================================================================
# Release
# ============================================================================

clean: ## Remove build artifacts
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml

build: clean ## Build wheel + sdist
	uv build

release-check: check security build ## Pre-release sanity check (check + security + build + twine)
	uv tool run twine check dist/*

publish: build ## Publish to PyPI
	uv publish
