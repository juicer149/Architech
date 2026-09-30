#!/usr/bin/env python3
# ================================================================
# scripts/benchmark_codex_vs_raw.py
# ================================================================
"""
Microbenchmark: RAW Python vs Codex (callable-mode).

Focus:
    • steady-state happy path
    • control-flow overhead (fallback / OR)
    • exception-as-value routing vs raising (via policy)

Important:
    - Codex is executed in callable-mode (RETURN outputs)
    - No descriptors, no __dict__ instances
    - Codex steps NEVER raise; they return Exception objects
    - Raising is handled only via policy (post-hook)

Env vars:
    BENCH_WARMUP   (default: 1000)
    BENCH_ITERS    (default: 20000)
    BENCH_RUNS     (default: 5)
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable, List, Tuple, Literal

# ---------------------------------------------------------------------
# Ensure repo root is on sys.path
# ---------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---------------------------------------------------------------------
# Architech imports
# ---------------------------------------------------------------------
from dsl import PhaseToken
from codex import Codex
from codex.ir import Phase
from codex.ir.output import Output, RETURN
from codex.ir.config import PhaseConfig
from codex.lang import WARNING, ERROR


# ================================================================
# Dummy Codex-style steps (return Exception objects)
# ================================================================

def normalize_email(x: str) -> str:
    return x.strip().lower()


def validate_at(x: str) -> str | BaseException:
    if "@" not in x:
        return ValueError("missing @")
    return x


def mask_local(x: str) -> str:
    _, _, domain = x.partition("@")
    return f"***@{domain}"


def always_fail(_: str) -> BaseException:
    return ValueError("fail")


def accept_any(x: str) -> str:
    return x.lower()


def return_exception(_: str) -> BaseException:
    return ValueError("boom")


# ================================================================
# Raw reference implementations (same semantics)
# ================================================================

def raw_set(x: str) -> str:
    x = normalize_email(x)
    out = validate_at(x)
    if isinstance(out, BaseException):
        raise out
    return out


def raw_set_get(x: str) -> str:
    x = normalize_email(x)
    out = validate_at(x)
    if isinstance(out, BaseException):
        raise out
    return mask_local(out)


def raw_fallback(x: str) -> str:
    out = always_fail(x)
    if isinstance(out, BaseException):
        return accept_any(x)
    return out  # pragma: no cover


def raw_or_short(x: str) -> str:
    out = validate_at(x)
    if isinstance(out, BaseException):
        return accept_any(x)
    return out


def raw_exception_value(_: str) -> BaseException:
    return ValueError("boom")


def raw_exception_raise(_: str) -> None:
    raise ValueError("boom")


# ================================================================
# Codex builder (callable-mode)
# ================================================================

ExcMode = Literal["return", "raise"]


def _raise_if_exception(value: Any, *_):
    if isinstance(value, BaseException):
        raise value
    return value


def build_codex_callable(
    *,
    set_section,
    get_section=None,
    exc_mode: ExcMode = "return",
) -> Callable[[str], Any]:

    post = _raise_if_exception if exc_mode == "raise" else None

    overrides = {
        Phase.SET: PhaseConfig(
            phase=Phase.SET,
            write=Output(False, True, RETURN),
            exc=Output(True, True, RETURN),
            post=post,
        ),
        Phase.GET: PhaseConfig(
            phase=Phase.GET,
            write=Output(False, True, RETURN),
            exc=Output(True, True, RETURN),
            post=post,
        ),
    }

    sections = [set_section]
    has_get = get_section is not None
    if has_get:
        sections.append(get_section)

    codex = Codex(*sections, overrides=overrides)

    def run(x: str):
        x = codex._run_phase(Phase.SET, None, x)
        if has_get:
            x = codex._run_phase(Phase.GET, None, x)
        return x

    return run


# ================================================================
# Benchmark helpers
# ================================================================

@dataclass
class BenchConfig:
    warmup: int
    iters: int


def time_fn(fn, inputs, cfg):
    for _ in range(cfg.warmup):
        for x in inputs:
            try:
                fn(x)
            except Exception:
                pass

    start = time.perf_counter()
    for _ in range(cfg.iters):
        for x in inputs:
            try:
                fn(x)
            except Exception:
                pass
    return time.perf_counter() - start


def time_fn_multi(fn, inputs, cfg, runs):
    results = [time_fn(fn, inputs, cfg) for _ in range(runs)]
    results.sort()
    avg = sum(results) / len(results)
    mid = len(results) // 2
    median = results[mid] if len(results) % 2 else (results[mid - 1] + results[mid]) / 2
    return results[0], median, avg


def bench_case(name, raw_fn, codex_fn, inputs, cfg, runs):
    calls = len(inputs) * cfg.iters
    _, raw_med, _ = time_fn_multi(raw_fn, inputs, cfg, runs)
    _, cod_med, _ = time_fn_multi(codex_fn, inputs, cfg, runs)

    print(name)
    print(f"  Raw:   {raw_med:.6f}s  ({raw_med / calls * 1e6:.2f} µs/call)")
    print(f"  Codex: {cod_med:.6f}s  ({cod_med / calls * 1e6:.2f} µs/call)\n")


# ================================================================
# Main
# ================================================================

def main():
    warmup = int(os.environ.get("BENCH_WARMUP", "1000"))
    iters = int(os.environ.get("BENCH_ITERS", "20000"))
    runs = int(os.environ.get("BENCH_RUNS", "5"))

    cfg = BenchConfig(warmup, iters)

    inputs_ok = [
        " Foo@Example.com ",
        "bar@BAZ.com",
        "user@domain.se",
        "TEST@Example.ORG",
    ]

    inputs_bad = [
        "not-an-email",
        "also.bad",
        "missing_at",
    ]

    print("\n=== Codex vs Raw (callable-mode) ===")
    print(f"runs={runs}, warmup={warmup}, iters={iters}\n")

    SET = PhaseToken(Phase.SET)
    GET = PhaseToken(Phase.GET)

    bench_case(
        "SET only",
        raw_set,
        build_codex_callable(
            set_section=(SET >> normalize_email >> validate_at).to_section()
        ),
        inputs_ok,
        cfg,
        runs,
    )

    bench_case(
        "SET + GET",
        raw_set_get,
        build_codex_callable(
            set_section=(SET >> normalize_email >> validate_at).to_section(),
            get_section=(GET >> mask_local).to_section(),
        ),
        inputs_ok,
        cfg,
        runs,
    )

    bench_case(
        "Fallback (taken)",
        raw_fallback,
        build_codex_callable(
            set_section=(SET >> always_fail << accept_any).to_section()
        ),
        inputs_ok,
        cfg,
        runs,
    )

    bench_case(
        "OR (short-circuit)",
        raw_or_short,
        build_codex_callable(
            set_section=(SET >> validate_at | accept_any).to_section()
        ),
        inputs_ok,
        cfg,
        runs,
    )

    bench_case(
        "OR (fallback)",
        raw_or_short,
        build_codex_callable(
            set_section=(SET >> validate_at | accept_any).to_section()
        ),
        inputs_bad,
        cfg,
        runs,
    )

    bench_case(
        "Exception → VALUE",
        raw_exception_value,
        build_codex_callable(
            set_section=((SET >> return_exception) @ WARNING).to_section(),
            exc_mode="return",
        ),
        inputs_ok,
        cfg,
        runs,
    )

    low_cfg = BenchConfig(200, 3000)

    bench_case(
        "Exception → RAISE (policy)",
        raw_exception_raise,
        build_codex_callable(
            set_section=((SET >> return_exception) @ ERROR).to_section(),
            exc_mode="raise",
        ),
        inputs_ok,
        low_cfg,
        runs,
    )


if __name__ == "__main__":
    main()
