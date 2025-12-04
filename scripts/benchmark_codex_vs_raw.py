import time
import os
import sys
from dataclasses import dataclass
from typing import Callable, List, Any, Tuple

# Ensure repo root is on sys.path when running as a script
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex import SET, GET, WARN, IGNORE
from blueprint.pipeline.codex_pipeline import PipelineCompiler
from control.panopticon import Panopticon
from control.capture.capture import Capture


# Dummy validation functions
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


# Numeric conversion/validation functions
def to_int_conv(x: object) -> int:
    return int(x)


def validate_positive(x: int) -> int:
    if x < 0:
        raise ValueError("negative")
    return x


@dataclass
class BenchConfig:
    warmup: int = 500
    iters: int = 2000
    # strict toggle for codex
    strict: bool | None = None  # None = auto, True = strict, False = interpreted


def time_fn(fn: Callable[[Any], Any], inputs: List[Any], cfg: BenchConfig) -> float:
    # Warmup
    for _ in range(cfg.warmup):
        for s in inputs:
            try:
                fn(s)
            except Exception:
                pass
    # Timed
    start = time.perf_counter()
    for _ in range(cfg.iters):
        for s in inputs:
            try:
                fn(s)
            except Exception:
                pass
    end = time.perf_counter()
    return end - start


def time_fn_multi(fn: Callable[[Any], Any], inputs: List[Any], cfg: BenchConfig, runs: int) -> Tuple[float, float, float]:
    """Return (min, median, avg) over multiple runs to reduce variance."""
    results: List[float] = []
    for _ in range(runs):
        results.append(time_fn(fn, inputs, cfg))
    results.sort()
    total = sum(results)
    n = len(results)
    median = results[n // 2] if n % 2 == 1 else (results[n // 2 - 1] + results[n // 2]) / 2.0
    return (results[0], median, total / n)


def run_raw_validator(x: str) -> str:
    # Simulate typical if/try validation flow
    x = normalize_email(x)
    if "@" not in x:
        raise ValueError("missing @")
    return mask_local(x)


def build_email_pipelines(strict: bool | None):
    b = build_codex_binding(
        [
            SET(strict=strict) >> normalize_email >> validate_at | IGNORE,
            GET(strict=strict) >> mask_local | IGNORE,
        ],
        domain="User.email",
        config=CodexConfig(strict=strict),
    )
    compiler = PipelineCompiler()
    pan = None if (strict is True) else Panopticon(capture=Capture())
    pipelines = compiler.build_pipeline(binding=b, panopticon=pan)
    return pipelines[Phase.SET][0], pipelines[Phase.GET][0]


def run_codex_validator_stages(
    set_stage: Callable[[str], str],
    get_stage: Callable[[str], str],
    x: str,
) -> str:
    v = set_stage(x)
    return get_stage(v)


def run_raw_numeric(x: object) -> int:
    v = int(x)
    if v < 0:
        raise ValueError("negative")
    return v


def build_numeric_pipelines(strict: bool | None):
    b = build_codex_binding(
        [
            SET(strict=strict) >> to_int_conv >> validate_positive | IGNORE,
            GET(strict=strict) >> (lambda x: x) | IGNORE,
        ],
        domain="User.age",
        config=CodexConfig(strict=strict),
    )
    compiler = PipelineCompiler()
    pan = None if (strict is True) else Panopticon(capture=Capture())
    pipelines = compiler.build_pipeline(binding=b, panopticon=pan)
    return pipelines[Phase.SET][0], pipelines[Phase.GET][0]


def run_codex_numeric_stages(
    set_stage: Callable[[object], int],
    get_stage: Callable[[int], int],
    x: object,
) -> int:
    v = set_stage(x)
    return get_stage(v)


def main():
    # Allow simple overrides via env vars
    warmup = int(os.environ.get("BENCH_WARMUP", "500"))
    iters = int(os.environ.get("BENCH_ITERS", "2000"))
    cfg = BenchConfig(warmup=warmup, iters=iters)
    runs = int(os.environ.get("BENCH_RUNS", "5"))

    inputs_ok = ["Foo@Example.com", "bar@BAZ.com"]
    inputs_bad = ["invalid", "no-at-symbol"]
    inputs = inputs_ok + inputs_bad

    # Numeric inputs including conversion case
    num_inputs_ok = [1, "3", 5]
    num_inputs_bad = ["-2", -1]
    num_inputs = num_inputs_ok + num_inputs_bad

    # Build two codex variants: strict=True and strict=False
    set_strict, get_strict = build_email_pipelines(strict=True)
    set_interp, get_interp = build_email_pipelines(strict=False)

    # FAST codex pipelines: strict=True, no semantics
    fb = build_codex_binding(
        [
            SET(strict=True) >> normalize_email >> validate_at,
            GET(strict=True) >> mask_local,
        ],
        domain="User.email",
        config=CodexConfig(strict=True),
    )
    compiler_fast = PipelineCompiler()
    pipelines_fast = compiler_fast.build_pipeline(binding=fb, panopticon=None)
    set_fast, get_fast = pipelines_fast[Phase.SET][0], pipelines_fast[Phase.GET][0]

    num_set_strict, num_get_strict = build_numeric_pipelines(strict=True)

    print("Benchmark: raw vs codex (WARN semantics; compare strict=True vs strict=False)")

    # Pre-check happy-path equality (email)
    assert run_raw_validator("Foo@Example.com") == run_codex_validator_stages(
        set_strict, get_strict, "Foo@Example.com"
    )
    # Pre-check conversion equality (numeric: "3" -> 3)
    assert run_raw_numeric("3") == run_codex_numeric_stages(
        num_set_strict, num_get_strict, "3"
    )

    raw_min, raw_med, raw_avg = time_fn_multi(lambda s: run_raw_validator(s), inputs, cfg, runs)
    strict_min, strict_med, strict_avg = time_fn_multi(
        lambda s: run_codex_validator_stages(set_strict, get_strict, s),
        inputs,
        cfg,
        runs,
    )
    interp_min, interp_med, interp_avg = time_fn_multi(
        lambda s: run_codex_validator_stages(set_interp, get_interp, s),
        inputs,
        cfg,
        runs,
    )
    fast_min, fast_med, fast_avg = time_fn_multi(
        lambda s: run_codex_validator_stages(set_fast, get_fast, s),
        inputs,
        cfg,
        runs,
    )

    # Numeric timings
    raw_num_min, raw_num_med, raw_num_avg = time_fn_multi(lambda s: run_raw_numeric(s), num_inputs, cfg, runs)
    codex_num_min, codex_num_med, codex_num_avg = time_fn_multi(
        lambda s: run_codex_numeric_stages(num_set_strict, num_get_strict, s),
        num_inputs,
        cfg,
        runs,
    )

    per_call = len(inputs) * cfg.iters
    print(f"Runs: {runs}; Warmup: {cfg.warmup}; Iters: {cfg.iters}")
    print(f"Raw total (median):           {raw_med:.6f}s for {per_call} calls")
    print(f"Codex strict total (median):  {strict_med:.6f}s for {per_call} calls")
    print(f"Codex interp total (median):  {interp_med:.6f}s for {per_call} calls")
    print(f"Codex FAST total (median):    {fast_med:.6f}s for {per_call} calls")
    print(f"Raw avg (per-call, median):            {raw_med / per_call * 1e6:.2f} µs/call")
    print(f"Codex strict avg (per-call, median):   {strict_med / per_call * 1e6:.2f} µs/call")
    print(f"Codex interp avg (per-call, median):   {interp_med / per_call * 1e6:.2f} µs/call")
    print(f"Codex FAST avg (per-call, median):     {fast_med / per_call * 1e6:.2f} µs/call")

    # Numeric report
    per_call_num = len(num_inputs) * cfg.iters
    print("\nNumeric conversion/validation:")
    print(f"Raw total (median):           {raw_num_med:.6f}s for {per_call_num} calls")
    print(f"Codex strict total (median):  {codex_num_med:.6f}s for {per_call_num} calls")
    print(f"Raw avg (per-call, median):            {raw_num_med / per_call_num * 1e6:.2f} µs/call")
    print(
        f"Codex strict avg (per-call, median):   {codex_num_med / per_call_num * 1e6:.2f} µs/call"
    )


if __name__ == "__main__":
    main()
