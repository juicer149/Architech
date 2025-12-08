#!/usr/bin/env python3
# ================================================================
# scripts/benchmark_codex_strict.py
# ================================================================
"""
Microbenchmark: raw vs Codex (strict + semantic) på happy path.

Fokuserar på att mäta *engine-overhead* snarare än Python-raise/catch.

Vi benchmar:

1) SET-only (ingen GET-fas)
   - raw_set_only
   - codex_set_only (strict=True, utan semantik)
   - codex_set_only (strict=True, med semantik-taggar)
   - codex_set_only (semantic-mode, strict=False)

2) SET+GET (båda faser per call)
   - raw_full (normalize + validate + mask)
   - codex_full (samma tre steg via Codex)

Alla benchmarks körs med BARA giltiga inputs för att undvika
exception-path i hot loop.

Environment-variabler:
    BENCH_WARMUP  (default: 500)
    BENCH_ITERS   (default: 2000)
    BENCH_RUNS    (default: 5)
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

from dsl import PhaseTokenBase, StepChain  # type: ignore
from codex.models import Phase, build_codex_spec, CodexConfig  # type: ignore
from codex.engine import CodexEngine  # type: ignore
from codex.constants import WARN, IGNORE  # type: ignore


# ================================================================
# Dummy functions (samma som dina)
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
# Raw implementations
# ================================================================

def raw_email_set_only(x: str) -> str:
    """
    Motsvarar SET-pipeline:
        normalize_email >> validate_at
    """
    x = normalize_email(x)
    x = validate_at(x)
    return x


def raw_email_full(x: str) -> str:
    """
    Motsvarar SET + GET:
        SET: normalize_email >> validate_at
        GET: mask_local
    """
    x = normalize_email(x)
    x = validate_at(x)
    x = mask_local(x)
    return x


# ================================================================
# Codex builders
# ================================================================

@dataclass
class EmailCodexStages:
    set_stage: Callable[[str], str]
    get_stage: Optional[Callable[[str], str]]  # None om GET saknas


def build_email_codex(
    *,
    strict: Optional[bool],
    semantic: bool,
    include_get: bool,
) -> EmailCodexStages:
    """
    Bygger en CodexEngine för email:
        SET: normalize_email >> validate_at [| semantic?]
        GET: mask_local [| semantic?] (valfritt)
    """
    SET = PhaseTokenBase(Phase.SET)
    GET = PhaseTokenBase(Phase.GET)

    # SET chain
    set_chain: StepChain = (SET >> normalize_email) >> validate_at
    if semantic:
        set_chain = set_chain | WARN  # eller IGNORE/WARN, spelar ingen roll för overhead

    # GET chain (valfri)
    if include_get:
        get_chain: StepChain = GET >> mask_local
        if semantic:
            get_chain = get_chain | IGNORE
        sections = (set_chain.to_section(), get_chain.to_section())
    else:
        sections = (set_chain.to_section(),)

    spec = build_codex_spec(sections)
    engine = CodexEngine(spec, CodexConfig(strict=strict))

    def set_stage(v: str) -> str:
        return engine.run_phase(Phase.SET, v)

    if include_get:
        def get_stage(v: str) -> str:
            return engine.run_phase(Phase.GET, v)
    else:
        get_stage = None

    return EmailCodexStages(set_stage=set_stage, get_stage=get_stage)


# ================================================================
# Bench helpers
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
    Return (min, median, avg) över flera körningar.
    """
    results: List[float] = []
    for _ in range(runs):
        results.append(time_fn(fn, inputs, cfg))

    results.sort()
    total = sum(results)
    n = len(results)
    median = results[n // 2] if n % 2 == 1 else (results[n // 2 - 1] + results[n // 2]) / 2.0
    return results[0], median, total / n


# ================================================================
# Wrapper runt codex stages
# ================================================================

def wrap_codex_set_only(stages: EmailCodexStages) -> Callable[[str], str]:
    def fn(x: str) -> str:
        return stages.set_stage(x)
    return fn


def wrap_codex_full(stages: EmailCodexStages) -> Callable[[str], str]:
    if stages.get_stage is None:
        raise RuntimeError("GET-stage saknas i wrap_codex_full")

    def fn(x: str) -> str:
        v = stages.set_stage(x)
        return stages.get_stage(v)
    return fn


# ================================================================
# Main benchmark
# ================================================================

def main() -> None:
    # Environment-konfig
    warmup = int(os.environ.get("BENCH_WARMUP", "500"))
    iters = int(os.environ.get("BENCH_ITERS", "2000"))
    runs = int(os.environ.get("BENCH_RUNS", "5"))
    cfg = BenchConfig(warmup=warmup, iters=iters)

    # ENDAST giltiga inputs för att undvika raise-path
    inputs_ok = [
        "Foo@Example.com",
        "bar@BAZ.com",
        " user@domain.se ",
        "TEST@Example.ORG",
    ]

    per_call = len(inputs_ok) * cfg.iters

    print("Benchmark: RAW vs Codex (strict/semantic) — HAPPY PATH ONLY")
    print(f"Runs: {runs}; Warmup: {cfg.warmup}; Iters: {cfg.iters}")
    print()

    # ------------------------------------------------------------
    # 1. SET-only
    # ------------------------------------------------------------
    print("=== SET-only (ingen GET) ===")

    raw_min, raw_med, raw_avg = time_fn_multi(raw_email_set_only, inputs_ok, cfg, runs)

    stages_strict_no_sem = build_email_codex(strict=True, semantic=False, include_get=False)
    stages_strict_sem = build_email_codex(strict=True, semantic=True, include_get=False)
    stages_semantic = build_email_codex(strict=False, semantic=True, include_get=False)

    codex_strict_no_sem = wrap_codex_set_only(stages_strict_no_sem)
    codex_strict_sem = wrap_codex_set_only(stages_strict_sem)
    codex_semantic = wrap_codex_set_only(stages_semantic)

    s_min, s_med, s_avg = time_fn_multi(codex_strict_no_sem, inputs_ok, cfg, runs)
    ss_min, ss_med, ss_avg = time_fn_multi(codex_strict_sem, inputs_ok, cfg, runs)
    si_min, si_med, si_avg = time_fn_multi(codex_semantic, inputs_ok, cfg, runs)

    print(f"[SET] Raw total (median):                {raw_med:.6f}s for {per_call} calls")
    print(f"[SET] Codex strict (no semantics):       {s_med:.6f}s for {per_call} calls")
    print(f"[SET] Codex strict (with semantics):     {ss_med:.6f}s for {per_call} calls")
    print(f"[SET] Codex semantic-mode (strict=False):{si_med:.6f}s for {per_call} calls")
    print(f"[SET] Raw avg (per-call, median):                 {raw_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET] Codex strict no-semantics avg:              {s_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET] Codex strict + semantics avg:               {ss_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET] Codex semantic-mode avg:                    {si_med / per_call * 1e6:.2f} µs/call")
    print()

    # ------------------------------------------------------------
    # 2. SET + GET
    # ------------------------------------------------------------
    print("=== SET + GET (full pipeline) ===")

    raw_full_min, raw_full_med, raw_full_avg = time_fn_multi(raw_email_full, inputs_ok, cfg, runs)

    stages_strict_no_sem_full = build_email_codex(strict=True, semantic=False, include_get=True)
    stages_strict_sem_full = build_email_codex(strict=True, semantic=True, include_get=True)
    stages_semantic_full = build_email_codex(strict=False, semantic=True, include_get=True)

    codex_strict_no_sem_full = wrap_codex_full(stages_strict_no_sem_full)
    codex_strict_sem_full = wrap_codex_full(stages_strict_sem_full)
    codex_semantic_full = wrap_codex_full(stages_semantic_full)

    s2_min, s2_med, s2_avg = time_fn_multi(codex_strict_no_sem_full, inputs_ok, cfg, runs)
    ss2_min, ss2_med, ss2_avg = time_fn_multi(codex_strict_sem_full, inputs_ok, cfg, runs)
    si2_min, si2_med, si2_avg = time_fn_multi(codex_semantic_full, inputs_ok, cfg, runs)

    print(f"[SET+GET] Raw total (median):                {raw_full_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Codex strict (no semantics):       {s2_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Codex strict (with semantics):     {ss2_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Codex semantic-mode (strict=False):{si2_med:.6f}s for {per_call} calls")
    print(f"[SET+GET] Raw avg (per-call, median):                 {raw_full_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET+GET] Codex strict no-semantics avg:              {s2_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET+GET] Codex strict + semantics avg:               {ss2_med / per_call * 1e6:.2f} µs/call")
    print(f"[SET+GET] Codex semantic-mode avg:                    {si2_med / per_call * 1e6:.2f} µs/call")


if __name__ == "__main__":
    main()
