# Architech

An experiment in designing a small DSL for attribute pipelines in Python:
declare how a value is validated and transformed when it is written or
read, how serious each failure is, and (in v4) where the result goes.

```python
class User:
    name  = StdCodex((SET >> strip >> non_empty) @ ERROR, (GET >> normalize))
    age   = IS_INT + POSITIVE + IN_RANGE(0, 150)
    email = CLEAN_EMAIL
```

## Steps

A step is a plain function that takes the current value and returns:

| Return | Meaning |
|--------|---------|
| `None` | success, value unchanged |
| a value | success, value replaced |
| an `Exception` instance | soft failure; the pipeline decides what happens |

Returning the exception is the preferred way to fail: it is cheaper than
raising. A step may also raise; the exception is caught and handled the
same way, so severity still decides the outcome. Only `KeyboardInterrupt`
and `SystemExit` are never caught.

```python
def upper(v):
    return v.upper()

def no_digits(v):
    if any(c.isdigit() for c in v):
        return ValueError(f"digits not allowed: {v!r}")
```

## The language

| Syntax | Meaning |
|--------|---------|
| `SET >> f >> g` | on write, run `f`, then `g` |
| `GET >> f` | on read, run `f` on the stored value |
| `f << repair` | if `f` fails, run `repair` and try `f` again on the result |
| `f \| g` | alternatives: the first that succeeds wins |
| `(…) @ ERROR` | what a failure means (see below) |
| `A + B` | merge two rule sets; they run in order |

| Severity | On failure |
|----------|------------|
| none | strict mode: the failure is raised as-is |
| `ERROR` / `FATAL` | raise (`RuntimeError` / `FatalError`); the attribute keeps its old value |
| `WARN` / `INFO` | print a message and keep the value from before the failing step |
| `IGNORE` | do nothing |

## Example

```python
from stdlib.codex import StdCodex, SET, GET, ERROR, WARN, IS_INT, POSITIVE, IN_RANGE, CLEAN_EMAIL
from stdlib.codex.transformers.text import strip, normalize
from stdlib.codex.validators.text import non_empty

def upper(v):
    return v.upper()

def no_digits(v):
    if any(c.isdigit() for c in v):
        return ValueError(f"digits not allowed: {v!r}")

def is_code(v):
    if not (len(v) == 3 and v.isalpha()):
        return ValueError(f"not a 3-letter code: {v!r}")

def to_code(v):                     # repair: cut to three letters
    return v[:3]

def from_number(v):
    return {"1": "one", "2": "two", "3": "three"}.get(v) or ValueError(f"unknown: {v!r}")

def from_word(v):
    return v if v in ("one", "two", "three") else ValueError(f"unknown: {v!r}")


class Product:
    sku      = StdCodex(SET >> strip >> upper)
    currency = StdCodex((SET >> strip >> upper >> is_code << to_code) @ ERROR)
    size     = StdCodex((SET >> from_number | from_word) @ ERROR)
    name     = StdCodex((SET >> strip >> no_digits) @ ERROR, (GET >> normalize))
    note     = StdCodex((SET >> strip >> non_empty) @ WARN, default="")
    stock    = IS_INT + POSITIVE + IN_RANGE(0, 10_000)
    email    = CLEAN_EMAIL


p = Product()

p.sku = "  ab-12 "            # p.sku      -> 'AB-12'
p.sku = 123                   # ValueError: Expected string, got int   (strict mode)

p.currency = " sek "          # p.currency -> 'SEK'
p.currency = "euro"           # p.currency -> 'EUR'   (is_code failed, to_code repaired it)

p.size = "2"                  # p.size     -> 'two'   (from_number)
p.size = "three"              # p.size     -> 'three' (from_number failed, from_word succeeded)

p.name = " Ada "              # p.name     -> 'ada'   (stored 'Ada', lowercased on read)
p.name = "R2D2"               # RuntimeError: [error] digits not allowed: 'R2D2' ...
                              # p.name     -> 'ada'   (unchanged)

p.note = "   "                # prints: [warn] value must not be empty ...
                              # p.note     -> ''

p.stock = "42"                # p.stock    -> 42      (IS_INT converted it)
p.stock = "-5"                # RuntimeError: [error] Expected positive number, got -5 ...

p.email = " Ada@Example.COM " # p.email    -> 'ada@example.com'
```

### Two precedence traps

Python's operator precedence is fixed, so:

- `@` binds tighter than `>>`. Always parenthesize: `(SET >> f >> g) @ ERROR`.
- `|` binds looser than `>>`. `SET >> a | b >> c` fails with a `TypeError`;
  write `(SET >> a | b) >> c`.

## Performance

Valid data is assumed to be the common case, so that is what is fast.
A phase made only of plain steps is flattened into a single loop the
first time the attribute is used; after that a valid assignment costs
well under a microsecond, slightly faster than pydantic's
`validate_assignment` for a single field. (Pydantic's strength is
parsing whole models from dicts or JSON, which this does not measure.)

Failures cost more on purpose. The phase is re-run through the full
engine to apply severity, fallbacks and alternatives and to build the
message. Returning an exception from a step is cheaper than raising
one, which is why returning is the convention.

`make bench-attr` (Python 3.12, one e-mail field: strip, lowercase, check `@`):

```
plain attribute (no validation)             0.03 µs      1.0x
hand-written @property                      0.19 µs      5.5x
pydantic validate_assignment                1.00 µs     28.7x
Architech strict                            0.70 µs     20.1x
Architech @ ERROR                           0.68 µs     19.5x
Architech @ WARN                            0.70 µs     20.0x
@property, invalid (raises)                 0.48 µs     13.7x
pydantic, invalid (raises)                  1.48 µs     42.7x
Architech @ ERROR, invalid (raises)         7.28 µs    209.4x
Architech @ WARN, invalid (prints)          6.80 µs    195.8x
```

## Direction

The goal for v4 is to let a data object describe a whole flow: raw
values come in, the rules live on the attributes, and the validated
result is routed on to where it is used, instead of only being stored
on the attribute.

Sketch (not runnable yet, syntax may change):

```python
class Argon2Policy:
    time_cost = Codex(
        (SET >> to_int >> in_range(1, 10)) @ ERROR,   # hard limits
        (SET >> in_range(2, 6)) @ WARN,               # recommendation
        write=TO_BACKEND,                             # route the result
    )
    memory_cost = Codex(...)
```

The backend then only ever receives values that have passed the policy
and needs no validation of its own. Reading the policy class top to
bottom tells you everything about the data. The same pattern fits in
front of a database or an API.

The routing has to stay visible in the class definition. An assignment
that silently writes somewhere else is hard to debug, so where a value
goes should be as explicit as how it is validated.

The first v4 milestone is exactly this example working end to end: a
valid value reaches the backend, an invalid one raises and never does.

## Layout

- `dsl/`: syntax only (phase tokens and the operators above), no semantics
- `codex/`: turns DSL expressions into a spec and runs it as a descriptor
- `stdlib/`: validators, transformers and ready-made rules (`IS_INT`, `CLEAN_EMAIL`, …)
- `scripts/`: benchmarks and a line counter
- `.history/`: notes per version

## Status

An experiment, not a library to depend on. There are no users and no
stability promises.

- `main` is v3: works, 49 tests, pure standard library.
- `wip/v4` is an unfinished redesign: compiler → IR → runtime layers, a
  `DELETE` phase, nested rules, and output routing (see Direction). The
  compiler and engine run; the package does not import yet.

The ideas started as `meta/` inside
[securitykit](https://github.com/juicer149/securitykit).

## Running

There is no package to install; run from the repository root.

```bash
make install       # .venv with pytest
make test
make bench-attr    # attribute benchmark (pip install pydantic in .venv to include it)
make bench         # engine-level benchmark

PYTHONPATH=. .venv/bin/python your_script.py
```

## License

MIT, see [LICENSE](LICENSE).
