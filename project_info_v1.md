## LOC Output
###########################################
#           Lines of Code (LOC)           #
###########################################

blueprint:
    +---------------+-------+-------+
    | Category      | Lines | Chars |
    +---------------+-------+-------+
    | Total         |  1568 | 46870 |
    | Documentation |   535 | 14776 |
    | Comments      |   166 |  9286 |
    | Logical       |   657 | 22598 |
    +---------------+-------+-------+

    +----------------------------+--------------+--------------+--------------+
    | File                       |     Total      |    Logical     | Documentation  |
    +----------------------------+-------+-------+-------+-------+-------+-------+
    |                            | Lines | Chars | Lines | Chars | Lines | Chars |
    +----------------------------+-------+-------+-------+-------+-------+-------+
    | __init__.py                |     0 |     0 |     0 |     0 |     0 |     0 |
    | codex/__init__.py          |    89 |  1990 |    41 |   696 |    33 |   915 |
    | codex/codex.py             |   250 |  7341 |    88 |  3412 |   114 |  2831 |
    | codex/constants.py         |    56 |  1806 |    13 |   349 |    18 |   488 |
    | codex/factory.py           |   310 | 10183 |   185 |  6702 |    63 |  1884 |
    | codex/models.py            |   216 |  5567 |    40 |  1127 |   119 |  3197 |
    | dsl/__init__.py            |    24 |   578 |     8 |   176 |    11 |   238 |
    | dsl/nodes.py               |    44 |  1084 |    13 |   345 |    20 |   572 |
    | dsl/phase_token.py         |    48 |  1498 |    22 |   822 |    14 |   502 |
    | dsl/protocol.py            |    53 |  1606 |    16 |   564 |    20 |   728 |
    | dsl/syntax.py              |    96 |  2941 |    41 |  1432 |    30 |   682 |
    | linker/__init__.py         |    12 |   417 |     2 |   131 |     5 |   119 |
    | linker/codex_binding.py    |    52 |  1155 |    31 |   806 |     8 |   169 |
    | pipeline/__init__.py       |    12 |   433 |     2 |   136 |     5 |   128 |
    | pipeline/codex_pipeline.py |   306 | 10271 |   155 |  5900 |    75 |  2323 |
    +----------------------------+-------+-------+-------+-------+-------+-------+

control:
    +---------------+-------+-------+
    | Category      | Lines | Chars |
    +---------------+-------+-------+
    | Total         |  2015 | 59087 |
    | Documentation |   824 | 24442 |
    | Comments      |   170 |  9218 |
    | Logical       |   769 | 25175 |
    +---------------+-------+-------+

    +------------------------------+--------------+--------------+--------------+
    | File                         |     Total      |    Logical     | Documentation  |
    +------------------------------+-------+-------+-------+-------+-------+-------+
    |                              | Lines | Chars | Lines | Chars | Lines | Chars |
    +------------------------------+-------+-------+-------+-------+-------+-------+
    | capture/__init__.py          |    56 |  1411 |    26 |   619 |    24 |   615 |
    | capture/capture.py           |   192 |  5961 |    99 |  3728 |    51 |  1353 |
    | capture/config.py            |    60 |  2094 |    14 |   489 |    33 |  1303 |
    | capture/context.py           |    72 |  1970 |    25 |   814 |    36 |   975 |
    | capture/models.py            |   255 |  7650 |    94 |  3077 |   109 |  3570 |
    | capture/post.py              |   133 |  3564 |    64 |  1727 |    44 |  1363 |
    | capture/pre.py               |    49 |  1402 |    22 |   673 |    15 |   492 |
    | config.py                    |   223 |  7122 |    34 |   992 |   149 |  5058 |
    | defaults.py                  |     5 |   160 |     3 |   137 |     0 |     0 |
    | effect/__init__.py           |    93 |  2105 |    29 |   539 |    55 |  1334 |
    | effect/effect.py             |   211 |  6515 |    60 |  1913 |   111 |  3478 |
    | effect/executor.py           |   151 |  3603 |    26 |   728 |    90 |  2189 |
    | effect/formatter.py          |   145 |  3809 |    34 |  1288 |    73 |  1818 |
    | panopticon.py                |   209 |  7323 |   139 |  5325 |    16 |   522 |
    | semantics/__init__.py        |    26 |   479 |    18 |   233 |     3 |    78 |
    | semantics/codex_semantics.py |   135 |  3919 |    82 |  2893 |    15 |   294 |
    +------------------------------+-------+-------+-------+-------+-------+-------+

Total:
    +---------------+-------+--------+
    | Category      | Lines |  Chars |
    +---------------+-------+--------+
    | Total         |  3583 | 105957 |
    | Documentation |  1359 |  39218 |
    | Comments      |   336 |  18504 |
    | Logical       |  1426 |  47773 |
    +---------------+-------+--------+

## Benchmark Output
Benchmark: raw vs codex (WARN semantics; compare strict=True vs strict=False)
Runs: 5; Warmup: 500; Iters: 2000
Raw total (median):           0.003613s for 8000 calls
Codex strict total (median):  0.014917s for 8000 calls
Codex interp total (median):  0.376009s for 8000 calls
Codex FAST total (median):    0.014324s for 8000 calls
Raw avg (per-call, median):            0.45 µs/call
Codex strict avg (per-call, median):   1.86 µs/call
Codex interp avg (per-call, median):   47.00 µs/call
Codex FAST avg (per-call, median):     1.79 µs/call

Numeric conversion/validation:
Raw total (median):           0.002530s for 10000 calls
Codex strict total (median):  0.015236s for 10000 calls
Raw avg (per-call, median):            0.25 µs/call
Codex strict avg (per-call, median):   1.52 µs/call
