"""Attribute-level benchmark: Architech v3 vs plain Python (and pydantic if installed).

Run from the repo root:  PYTHONPATH=. .venv/bin/python scripts/bench_attr.py
"""
import contextlib, io, statistics, sys, timeit

from stdlib.codex import StdCodex, SET, ERROR, WARN

N, RUNS = 50_000, 7
VALID, INVALID = "  Ada@Example.COM ", "  not-an-email "

# Steps in Architech style: return None / a new value / an Exception
def strip(v):  return v.strip()
def lower(v):  return v.lower()
def has_at(v): return None if "@" in v else ValueError("missing @")


class Plain:
    __slots__ = ("email",)


class Prop:
    @property
    def email(self): return self._email
    @email.setter
    def email(self, v):
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("missing @")
        self._email = v


class CodexStrict:
    email = StdCodex(SET >> strip >> lower >> has_at)

class CodexError:
    email = StdCodex((SET >> strip >> lower >> has_at) @ ERROR)

class CodexWarn:
    email = StdCodex((SET >> strip >> lower >> has_at) @ WARN)


cases = [
    ("plain attribute (no validation)", Plain, VALID),
    ("hand-written @property", Prop, VALID),
    ("Architech strict", CodexStrict, VALID),
    ("Architech @ ERROR", CodexError, VALID),
    ("Architech @ WARN", CodexWarn, VALID),
    ("@property, invalid (raises)", Prop, INVALID),
    ("Architech @ ERROR, invalid (raises)", CodexError, INVALID),
    ("Architech @ WARN, invalid (prints)", CodexWarn, INVALID),
]

try:
    from pydantic import BaseModel, ConfigDict, field_validator

    class Pyd(BaseModel):
        model_config = ConfigDict(validate_assignment=True)
        email: str = "a@b"

        @field_validator("email")
        @classmethod
        def check(cls, v):
            v = v.strip().lower()
            if "@" not in v:
                raise ValueError("missing @")
            return v

    cases[2:2] = [("pydantic validate_assignment", Pyd, VALID)]
    cases.insert(-2, ("pydantic, invalid (raises)", Pyd, INVALID))
except ImportError:
    pass


def run(cls, value):
    obj = cls()

    def assign():
        try:
            obj.email = value
        except Exception:
            pass

    with contextlib.redirect_stdout(io.StringIO()):
        times = timeit.repeat(assign, number=N, repeat=RUNS)
    return statistics.median(times) / N * 1e6


print(f"Python {sys.version.split()[0]}, {N:,} assignments x {RUNS} runs, median\n")
base = None
for label, cls, value in cases:
    us = run(cls, value)
    if base is None:
        base = us
    print(f"{label:<40} {us:7.2f} µs   {us / base:6.1f}x")
