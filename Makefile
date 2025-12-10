# Virtual environment
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

# Allow passing extra args after target name, e.g.:
#   make loc codex dsl
# Captures non-target words into ARGS.
ARGS := $(filter-out $@,$(MAKECMDGOALS))

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make venv          Create virtual environment and install deps"
	@echo "  make install       Install project in editable mode (dev + bench extras)"
	@echo "  make install-core  Install project in editable mode (core only)"
	@echo "  make test          Run test suite with pytest"
	@echo "  make lint          Run ruff linter"
	@echo "  make format        Auto-format code with black"
	@echo "  make typecheck     Run mypy type checks"
	@echo "  make bench         Run benchmark (pass args via ARGS='...')"
	@echo "  make clean         Remove caches, coverage data, and build artifacts"

venv:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv
	$(PIP) install -e ".[dev,bench]"

# Optional: core-only install (no algorithm deps)
install-core: venv
	@echo "  make bench         Run Codex benchmark (WARMUP/ITERS/RUNS overridable)"
	@echo "  make loc           Count LOC for folders. Usage:"
	@echo "                     make loc codex dsl tests"
	@echo "                     or: make loc DIRS=\"codex dsl\""
test:
	pytest -q --cov=codex --cov=dsl --cov=loader --cov-report=term-missing

lint:
	$(VENV)/bin/ruff check src tests_new

format:
	$(VENV)/bin/black src tests_new

typecheck:
	$(VENV)/bin/mypy src

BENCH_WARMUP ?= 3000
BENCH_ITERS  ?= 30000
BENCH_RUNS   ?= 7 
bench:
	BENCH_WARMUP=$(BENCH_WARMUP) BENCH_ITERS=$(BENCH_ITERS) BENCH_RUNS=$(BENCH_RUNS) \
	python3 scripts/benchmark_codex_vs_raw.py

LOC_DIRS ?=
loc:
	python3 scripts/loc.py $(if $(LOC_DIRS),$(LOC_DIRS),$(ARGS))

# Swallow extra words (like folder names) so Make doesn't error on them
%:
	@:

# Clean caches, coverage data, and build artifacts
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	find . -type d -name '.ruff_cache' -exec rm -rf {} +
	find . -type f -name '.coverage' -delete
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
