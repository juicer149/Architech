#!/usr/bin/env python3
# ================================================================
# scripts/benchmark_codex_vs_raw.py
# ================================================================
"""
Microbenchmark: RAW Python vs Codex (strict / semantic) on the happy path.

The goal is to measure *execution overhead* of Codex phases
compared to raw Python implementations, avoiding exception paths.

We benchmark:

1) SET-only (no GET phase)
    - raw_email_set_only
    - codex_set_only (strict=True, no semantics)
    - codex_set_only (strict=True, with semantics)
    - codex_set_only (semantic-mode: strict=False)

2) SET + GET (full pipeline)
    - raw_email_full   (normalize + validate + mask)
    - codex_full       (same behavior via Codex)

Environment variables:
    BENCH_WARMUP   (default: 500)
    BENCH_ITERS    (default: 2000)
    BENCH_RUNS     (default: 5)

This script intentionally does NOT disable Python's GC by default,
to match your request.
"""

import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable, List, Tuple, Optional

# Ensure repo root is on sys.path when running as a script
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# New DSL API (v3)
from dsl import StepChain, PhaseToken
from codex.models import Phase, build_codex_spec, CodexConfig
from codex.engine import CodexEngine
from codex.constants import WARN, IGNORE


# ================================================================
# Dummy transformations (happy-path only)
# ================================================================

def normalize_email(x: str) -> str:
    return x.strip().lower()

def validate_at(x: str) -> str:
    if "@" not in x:
        raise ValueError("missing @")
    return x

def mask_local(x: str) -> str:
    try:
        local, domain = x.split("@", 1)
    except ValueError:
        return x
    return f"***@{domain}"


# ================================================================
# Raw reference implementations
# ================================================================

def raw_email_set_only(x: str) -> str:
    """
    Equivalent to SET-phase:
        normalize_email >> validate_at
    """
    x = normalize_email(x)
    x = validate_at(x)
    return x


def raw_email_full(x: str) -> str:
    """
    Equivalent to SET + GET:
        SET: normalize_email >> validate_at
        GET: mask_local
    """
    x = normalize_email(x)
    x = validate_at(x)
    x = mask_local(x)
    return x


# ================================================================
# Codex builders (v3 DSL)
# ================================================================

@dataclass
class EmailCodexStages:
    set_stage: Callable[[str], str]
    get_stage: Optional[Callable[[str], str]]


def build_email_codex(
    *,
    strict: Optional[bool],
    semantic: bool,
    include_get: bool,
) -> EmailCodexStages:
    """
    Build a CodexEngine for:
        SET: normalize_email >> validate_at [semantic-tag optional]
        GET: mask_local [semantic-tag optional]
    """
    SET = PhaseToken(Phase.SET)
    GET = PhaseToken(Phase.GET)

    # --- SET chain -------------------------------------------------------
    set_chain: StepChain = (SET >> normalize_email) >> validate_at
    if semantic:
        set_chain = set_chain @ WARN

    # --- GET chain (optional) -------------------------------------------
    if include_get:
        get_chain: StepChain = GET >> mask_local
        if semantic:
            get_chain = get_chain @ IGNORE
        sections = (set_chain.to_section(), get_chain.to_section())
    else:
        sections = (set_chain.to_section(),)

    # Build Codex engine
    spec = build_codex_spec(sections)
    engine = CodexEngine(spec, CodexConfig(strict=strict))

    # Public API wrappers
    def set_stage(v: str) -> str:
        return engine.run_phase(Phase.SET, v)

    if include_get:
        def get_stage(v: str) -> str:
            return engine.run_phase(Phase.GET, v)
    else:
        get_stage = None

    return EmailCodexStages(set_stage=set_stage, get_stage=get_stage)


# ================================================================
# Benchmark helpers
# ================================================================

@dataclass
class BenchConfig:
    warmup: int = 1000
    iters: int = 10000


def time_fn(fn: Callable[[Any], Any], inputs: List[Any], cfg: BenchConfig) -> float:
    # Warmup
    for _ in range(cfg.warmup):
        for s in inputs:
            try:
                fn(s)
            except Exception:
                pass

    # Timed run
    start = time.perf_counter()
    for _ in range(cfg.iters):
        for s in inputs:
            try:
                fn(s)
            except Exception:
                pass
    end = time.perf_counter()

    return end - start


def time_fn_multi(
    fn: Callable[[Any], Any],
    inputs: List[Any],
    cfg: BenchConfig,
    runs: int,
) -> Tuple[float, float, float]:
    """
    Returns (min, median, avg) over multiple runs.
    """
    results: List[float] = [time_fn(fn, inputs, cfg) for _ in range(runs)]
    results.sort()
    avg = sum(results) / len(results)
    n = len(results)
    median = results[n // 2] if n % 2 else (results[n // 2] + results[n // 2 - 1]) / 2
    return results[0], median, avg


# ================================================================
# Wrappers for Codex
# ================================================================

def wrap_codex_set_only(stages: EmailCodexStages) -> Callable[[str], str]:
    return lambda x: stages.set_stage(x)

def wrap_codex_full(stages: EmailCodexStages) -> Callable[[str], str]:
    if stages.get_stage is None:
        raise RuntimeError("GET stage is missing in wrap_codex_full")

    return lambda x: stages.get_stage(stages.set_stage(x))


# ================================================================
# Main benchmark
# ================================================================

def main() -> None:
    warmup = int(os.environ.get("BENCH_WARMUP", "500"))
    iters = int(os.environ.get("BENCH_ITERS", "2000"))
    runs = int(os.environ.get("BENCH_RUNS", "5"))
    cfg = BenchConfig(warmup=warmup, iters=iters)

    # Only valid inputs (avoid exception path)
    inputs_ok = [
        "Foo@Example.com",
        "bar@BAZ.com",
        " user@domain.se ",
        "TEST@Example.ORG",
    ]

    per_call = len(inputs_ok) * cfg.iters

    print("Benchmark: RAW vs Codex (strict/semantic) — HAPPY PATH ONLY")
    print(f"Runs: {runs}; Warmup: {cfg.warmup}; Iters: {cfg.iters}\n")

    # ============================================================
    # SET-only
    # ============================================================
    print("=== SET-only ===")

    raw_min, raw_med, _ = time_fn_multi(raw_email_set_only, inputs_ok, cfg, runs)

    stages_strict_no_sem = build_email_codex(strict=True, semantic=False, include_get=False)
    stages_strict_sem    = build_email_codex(strict=True, semantic=True,  include_get=False)
    stages_semantic      = build_email_codex(strict=False, semantic=True, include_get=False)

    codex_strict_no_sem = wrap_codex_set_only(stages_strict_no_sem)
    codex_strict_sem    = wrap_codex_set_only(stages_strict_sem)
    codex_semantic      = wrap_codex_set_only(stages_semantic)

    s_min, s_med, _  = time_fn_multi(codex_strict_no_sem, inputs_ok, cfg, runs)
    ss_min, ss_med, _ = time_fn_multi(codex_strict_sem, inputs_ok, cfg, runs)
    si_min, si_med, _ = time_fn_multi(codex_semantic, inputs_ok, cfg, runs)

    print(f"[SET] Raw total (median):                {raw_med:.6f}s for {per_call} calls")
    print(f"[SET] Codex strict (no semantics):       {s_med:.6f}s for {per_call} calls")
    print(f"[SET] Codex strict (with semantics):     {ss_med:.6f}s for {per_call} calls")
    print(f"[SET] Codex semantic-mode (strict=False):{si_med:.6f}s for {per_call} calls")
    print(f"[SET] Raw avg (per-call, median):                 {raw_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET] Codex strict no-semantics avg:              {s_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET] Codex strict + semantics avg:               {ss_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET] Codex semantic-mode avg:                    {si_med / per_call * 1e6:.2f} µs/call\n")

    # ============================================================
    # SET + GET
    # ============================================================
    print("=== SET + GET (full pipeline) ===")

    raw2_min, raw2_med, _ = time_fn_multi(raw_email_full, inputs_ok, cfg, runs)

    stages_strict_no_sem_full = build_email_codex(strict=True,  semantic=False, include_get=True)
    stages_strict_sem_full    = build_email_codex(strict=True,  semantic=True,  include_get=True)
    stages_semantic_full      = build_email_codex(strict=False, semantic=True, include_get=True)

    codex_strict_no_sem_full = wrap_codex_full(stages_strict_no_sem_full)
    codex_strict_sem_full    = wrap_codex_full(stages_strict_sem_full)
    codex_semantic_full      = wrap_codex_full(stages_semantic_full)

    s2_min, s2_med, _  = time_fn_multi(codex_strict_no_sem_full, inputs_ok, cfg, runs)
    ss2_min, ss2_med, _ = time_fn_multi(codex_strict_sem_full, inputs_ok, cfg, runs)
    si2_min, si2_med, _ = time_fn_multi(codex_semantic_full, inputs_ok, cfg, runs)

    print(f"[SET+GET] Raw total (median):                {raw2_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Codex strict (no semantics):       {s2_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Codex strict (with semantics):     {ss2_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Codex semantic-mode (strict=False):{si2_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Raw avg (per-call, median):                 {raw2_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET+GET] Codex strict no-semantics avg:              {s2_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET+GET] Codex strict + semantics avg:               {ss2_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET+GET] Codex semantic-mode avg:                    {si2_med / per_call * 1e6:.2f} µs/call")


if __name__ == "__main__":
    main()
