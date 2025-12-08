python3 scripts/loc.py loc dsl codex bench
###########################################
#           Lines of Code (LOC)           #
###########################################

dsl:
    +---------------+-------+-------+
    | Category      | Lines | Chars |
    +---------------+-------+-------+
    | Total         |   294 |  8439 |
    | Documentation |   149 |  4218 |
    | Comments      |    15 |   808 |
    | Logical       |    96 |  3379 |
    +---------------+-------+-------+

    +----------------+--------------+--------------+--------------+
    | File           |     Total      |    Logical     | Documentation  |
    +----------------+-------+-------+-------+-------+-------+-------+
    |                | Lines | Chars | Lines | Chars | Lines | Chars |
    +----------------+-------+-------+-------+-------+-------+-------+
    | __init__.py    |    53 |  1600 |    13 |   306 |    35 |  1130 |
    | nodes.py       |    86 |  2193 |    16 |   474 |    59 |  1552 |
    | phase_token.py |    54 |  1661 |    19 |   755 |    24 |   733 |
    | protocol.py    |    34 |   831 |     9 |   260 |    16 |   403 |
    | syntax.py      |    67 |  2154 |    39 |  1584 |    15 |   400 |
    +----------------+-------+-------+-------+-------+-------+-------+

codex:
    +---------------+-------+-------+
    | Category      | Lines | Chars |
    +---------------+-------+-------+
    | Total         |   743 | 20532 |
    | Documentation |   185 |  5010 |
    | Comments      |    77 |  3883 |
    | Logical       |   362 | 11520 |
    +---------------+-------+-------+

    +--------------+--------------+--------------+--------------+
    | File         |     Total      |    Logical     | Documentation  |
    +--------------+-------+-------+-------+-------+-------+-------+
    |              | Lines | Chars | Lines | Chars | Lines | Chars |
    +--------------+-------+-------+-------+-------+-------+-------+
    | __init__.py  |    55 |  1184 |    23 |   350 |    26 |   667 |
    | codex.py     |   144 |  4200 |    65 |  2181 |    50 |  1465 |
    | constants.py |    47 |  1290 |    18 |   560 |    16 |   449 |
    | engine.py    |   299 |  8616 |   166 |  5628 |    32 |   817 |
    | models.py    |   122 |  3266 |    68 |  2089 |    17 |   520 |
    | semantics.py |    76 |  1976 |    22 |   712 |    44 |  1092 |
    +--------------+-------+-------+-------+-------+-------+-------+

Total:
    +---------------+-------+-------+
    | Category      | Lines | Chars |
    +---------------+-------+-------+
    | Total         |  1037 | 28971 |
    | Documentation |   334 |  9228 |
    | Comments      |    92 |  4691 |
    | Logical       |   458 | 14899 |
    +---------------+-------+-------+
make: 'dsl' is up to date.
make: 'codex' is up to date.
BENCH_WARMUP=500 BENCH_ITERS=2000 BENCH_RUNS=5 \
python3 scripts/benchmark_codex_vs_raw.py
Benchmark: RAW vs Codex (strict/semantic) — HAPPY PATH ONLY
Runs: 5; Warmup: 500; Iters: 2000

=== SET-only (ingen GET) ===
[SET] Raw total (median):                0.001934s for 8000 calls
[SET] Codex strict (no semantics):       0.015588s for 8000 calls
[SET] Codex strict (with semantics):     0.015542s for 8000 calls
[SET] Codex semantic-mode (strict=False):0.015353s for 8000 calls
[SET] Raw avg (per-call, median):                 0.24 µs/call
[SET] Codex strict no-semantics avg:              1.95 µs/call
[SET] Codex strict + semantics avg:               1.94 µs/call
[SET] Codex semantic-mode avg:                    1.92 µs/call

=== SET + GET (full pipeline) ===
[SET+GET] Raw total (median):                0.003488s for 8000 calls
[SET+GET] Codex strict (no semantics):       0.030181s for 8000 calls
[SET+GET] Codex strict (with semantics):     0.029371s for 8000 calls
[SET+GET] Codex semantic-mode (strict=False):0.030366s for 8000 calls
[SET+GET] Raw avg (per-call, median):                 0.44 µs/call
[SET+GET] Codex strict no-semantics avg:              3.77 µs/call
[SET+GET] Codex strict + semantics avg:               3.67 µs/call
[SET+GET] Codex semantic-mode avg:                    3.80 µs/call
