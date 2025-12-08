# ================================================================
# Architech/codex/codex.py
# ================================================================
"""
Codex — User-facing descriptor API.

Responsibility
--------------
Codex is the public interface for defining semantic pipelines on class
attributes. A Codex instance:

    1. Stores DSL sections (SET/GET pipelines)
    2. Performs strict-first evaluation when the attribute is read/written
    3. Delegates execution to CodexEngine
    4. Works as a descriptor:
            class X:
                email = Codex(SET >> normalize >> validate | ERROR)

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

from dsl import StepChain, SectionNode
from .models import (
    Phase,
    build_codex_spec,
    CodexConfig,
#    CodexSpec,
)
from .engine import CodexEngine


# Normalize user input from DSL
def _norm(x):
    if isinstance(x, StepChain):
        return x.to_section()
    if isinstance(x, SectionNode):
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
        DSL objects (StepChain or SectionNode)

    strict:
        - True  → disable semantics (strict mode)
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

    def __init__(self, *sections: Any, strict=None, default=None):
        self._sections = tuple(sections)
        self._strict = strict
        self._default = default

    # ---------------- descriptor -----------------

    def __set_name__(self, owner, name):
        self._name = name
        # Auto-inject a minimal __init__ for classes without one so that
        # a single positional argument can initialize this Codex-backed field.
        # This preserves user-defined __init__ if present.
        default_init = object.__init__
        owner_init = getattr(owner, "__init__", default_init)
        if owner_init is default_init:
            def __init__(inst, v=None, **kwargs):
                # Use object.__setattr__ to support frozen dataclasses.
                if v is not None:
                    object.__setattr__(inst, name, v)
                # Allow keyword initialization for other attributes
                for k, val in kwargs.items():
                    object.__setattr__(inst, k, val)
            owner.__init__ = __init__

    def _attr(self):
        if self._name is None:
            raise RuntimeError("Codex used before __set_name__.")
        return self._name

    def __get__(self, inst, owner):  # "owner" is not accessed
        if inst is None:
            return self
        eng = self._get_engine()
        internal = inst.__dict__.get(self._attr(), self._default)
        return eng.run_phase(Phase.GET, internal)

    def __set__(self, inst, value):
        eng = self._get_engine()
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

    def __add__(self, other):
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
