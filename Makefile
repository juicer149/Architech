VENV := .venv
PYTHON := $(VENV)/bin/python

.DEFAULT_GOAL := help

help:
	@echo "make install   Create .venv with pytest"
	@echo "make test      Run tests with coverage"
	@echo "make bench     Codex vs plain Python benchmark"
	@echo "make loc       Count lines, e.g. make loc DIRS=\"codex dsl\""
	@echo "make clean     Remove caches"

$(VENV):
	python3 -m venv $(VENV)

install: $(VENV)
	$(PYTHON) -m pip install --upgrade pip pytest pytest-cov

test:
	$(PYTHON) -m pytest -q

BENCH_WARMUP ?= 3000
BENCH_ITERS  ?= 30000
BENCH_RUNS   ?= 7
bench:
	BENCH_WARMUP=$(BENCH_WARMUP) BENCH_ITERS=$(BENCH_ITERS) BENCH_RUNS=$(BENCH_RUNS) \
	PYTHONPATH=. $(PYTHON) scripts/benchmark_codex_vs_raw.py

DIRS ?= codex dsl stdlib
loc:
	python3 scripts/loc.py $(DIRS)

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov

.PHONY: help install test bench loc clean

bench-attr:
	PYTHONPATH=. $(PYTHON) scripts/bench_attr.py
