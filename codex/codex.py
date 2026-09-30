# ================================================================
# architech/codex/codex.py
# ================================================================
"""
Codex — User-facing descriptor API.

Responsibility
--------------
Codex is the public interface for defining semantic pipelines on
class attributes. A Codex instance:

    1. Stores DSL sections (SET/GET pipelines)
    2. Performs strict-first evaluation when the attribute is read/written
    3. Delegates execution to CodexEngine
    4. Works as a descriptor:

            from codex import Codex, SET, GET, ERROR

            class X:
                email = Codex(
                    SET >> normalize >> validate @ ERROR,
                    GET >> normalize,
                )

Lifecycle
---------
    • __set_name__   → captures attribute name
    • __get__        → runs Phase.GET pipeline
    • __set__        → runs Phase.SET pipeline
    • _get_engine    → builds CodexSpec + CodexEngine on first use

Codex itself holds **no semantics**. It only:

    - Builds the spec
    - Chooses strict-mode or semantic-mode
    - Routes calls to the engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple

from dsl import StepChain, Section
from .models import (
    Phase,
    build_codex_spec,
    CodexConfig,
)
from .engine import CodexEngine


# Normalize user input from DSL or raw Section
def _norm(x: Any) -> Section:
    if isinstance(x, StepChain):
        return x.to_section()
    if isinstance(x, Section):
        return x
    raise TypeError(f"Invalid Codex element: {x!r}")


# ================================================================
# Codex descriptor
# ================================================================

@dataclass
class Codex:
    """
    High-level descriptor wrapping a semantic pipeline.

    Parameters
    ----------
    *sections:
        DSL objects (StepChain or Section)

    strict:
        - True  → disable semantics (strict mode only)
        - False → enable semantics
        - None  → auto: enable semantics if any Principle appears

    default:
        Default value returned before attribute is first set.
    """

    _sections: Tuple[Any, ...]
    _strict: Optional[bool]
    _default: Any
    _name: Optional[str] = None
    _engine: Optional[CodexEngine] = None

    def __init__(self, *sections: Any, strict: Optional[bool] = None, default: Any = None):
        self._sections = tuple(sections)
        self._strict = strict
        self._default = default

    # ---------------- descriptor -----------------

    def __set_name__(self, owner, name: str):
        self._name = name

        # Optional: inject a minimal __init__ for classes without one so that
        # a single positional argument can initialize this Codex-backed field.
        #
        # This preserves user-defined __init__ if present.
        default_init = object.__init__
        owner_init = getattr(owner, "__init__", default_init)
        if owner_init is default_init:

            def __init__(inst, v=None, **kwargs):
                if v is not None:
                    # Descriptor __set__ will run, which enforces Codex pipeline.
                    setattr(inst, name, v)
                for k, val in kwargs.items():
                    setattr(inst, k, val)

            owner.__init__ = __init__

    def _attr(self) -> str:
        if self._name is None:
            raise RuntimeError("Codex used before __set_name__.")
        return self._name

    def __get__(self, inst, owner=None):
        if inst is None:
            # Accessed on the class, return descriptor itself
            return self
        eng = self._get_engine()
        internal = inst.__dict__.get(self._attr(), self._default)
        if eng.fast_get is not None:
            return eng.run_fast(eng.fast_get, Phase.GET, internal)
        return eng.run_phase(Phase.GET, internal)

    def __set__(self, inst, value):
        eng = self._get_engine()
        if eng.fast_set is not None:
            res = eng.run_fast(eng.fast_set, Phase.SET, value)
        else:
            res = eng.run_phase(Phase.SET, value)
        inst.__dict__[self._attr()] = res

    # ---------------- engine ---------------------

    def _get_engine(self) -> CodexEngine:
        # Cached engine for speed
        if self._engine is not None:
            return self._engine

        nodes = tuple(_norm(x) for x in self._sections)
        spec = build_codex_spec(nodes)
        cfg = CodexConfig(strict=self._strict)

        self._engine = CodexEngine(spec, cfg)
        return self._engine

    # ---------------- composition ----------------

    def __add__(self, other: Any):
        """
        Merge two Codex definitions into one.

        Strict-mode is resolved by AND/OR rules:
            True + True   → True
            False + ?     → False
            None + X      → None (auto)
        """
        if not isinstance(other, Codex):
            return NotImplemented

        merged = Codex(
            *(self._sections + other._sections),
            strict=(
                False if self._strict is False or other._strict is False
                else True if self._strict is True and other._strict is True
                else None
            ),
            default=self._default,
        )
        return merged
