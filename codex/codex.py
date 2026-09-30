# =============================================================================
# architech/codex/codex.py
# =============================================================================
"""
(11) Codex — user-facing facade.

Codex is the public entry point to the Codex backend.

What Codex does
---------------
- Accepts DSL inputs:
  - dsl.Section
  - dsl.StepChain
  - nested Codex objects
  - iterables (list/tuple) of the above
- Compiles them into PhasePlans (IR)
- Exposes itself as a Python descriptor (via DescriptorRouting)
- Can also act as a callable Step inside another Codex pipeline

Descriptor execution model
--------------------------
A single descriptor call (__get__ / __set__ / __delete__) is treated as one
Codex execution boundary:

- A fresh ExecutionContext is created per descriptor call.
- One or more phases may run inside that boundary.
- Timing.PHASE effects are flushed once, at the end of the boundary.

This makes Timing meaningful:
- Timing.CLUSTER: apply immediately
- Timing.PHASE: defer until the descriptor call completes

Callable (Step) model
---------------------
When Codex is used as a Step (via __call__):
- ONLY Phase.SET is executed
- A fresh ExecutionContext is created per call
- Timing.PHASE effects are flushed at the end of the call
- No instance routing is performed (instance=None)

Key rules
---------
- If no Phase is specified in DSL, Phase.SET is assumed (handled by DSL).
- When Codex is used as a Step (__call__), ONLY Phase.SET is executed.
- Descriptor semantics apply only when Codex is bound on a class attribute.

Typical usage
-------------
from dsl import PhaseToken
from codex import Codex, Phase

SET = PhaseToken(Phase.SET)
GET = PhaseToken(Phase.GET)

NAME = Codex(
    (SET >> strip >> validate_name) @ "error",
    (GET >> normalize_name),
)

class User:
    name = NAME
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from dsl import Section, StepChain

from .compiler.compile import compile_sections
from .ir.config import PhaseConfig
from .ir.phase import Phase
from .ir.plan import PhasePlan
from .runtime.context import ExecutionContext
from .runtime.routing import DescriptorRouting


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_PHASE = Phase.SET


class Codex(DescriptorRouting):
    """
    Codex is both:
    - a descriptor (when bound to a class attribute)
    - a callable Step (when used inside another Codex pipeline)

    IMPORTANT:
    When used as a callable Step, Codex executes ONLY Phase.SET.
    """

    def __init__(
        self,
        *items: Any,
        overrides: Optional[Dict[Phase, PhaseConfig]] = None,
    ):
        sections: List[Section] = []

        def add_one(x: Any) -> None:
            if x is None:
                return

            # Flatten nested Codex
            if isinstance(x, Codex):
                sections.extend(x.sections)
                return

            # DSL StepChain
            if isinstance(x, StepChain):
                sections.append(x.to_section())
                return

            # DSL Section
            if isinstance(x, Section):
                sections.append(x)
                return

            # Iterable
            if isinstance(x, (list, tuple)):
                for y in x:
                    add_one(y)
                return

            raise TypeError(f"Unsupported Codex item: {type(x)!r} ({x!r})")

        for it in items:
            add_one(it)

        self._sections = tuple(sections)
        plans: Dict[Phase, PhasePlan] = compile_sections(self._sections)

        super().__init__(plans, overrides=overrides or {})

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def sections(self) -> tuple[Section, ...]:
        return self._sections

    # ------------------------------------------------------------------
    # Descriptor protocol
    # ------------------------------------------------------------------

    def __get__(self, instance: Any, owner: Optional[type] = None) -> Any:
        """
        Descriptor GET.

        - If accessed on the class (instance is None), return the descriptor.
        - Otherwise run Phase.GET within a single ExecutionContext boundary.
        """
        if instance is None:
            return self

        ctx = ExecutionContext()

        # Current stored value (if any) becomes the input to the GET pipeline.
        name = self._name  # set by __set_name__ in DescriptorRouting
        current = instance.__dict__.get(name, None) if name else None

        result = self._run_phase(
            phase=Phase.GET,
            instance=instance,
            value=current,
            ctx=ctx,
        )

        ctx.flush()
        return result

    def __set__(self, instance: Any, value: Any) -> None:
        """
        Descriptor SET.

        Runs Phase.SET within a single ExecutionContext boundary and flushes
        Timing.PHASE effects once at the end.
        """
        ctx = ExecutionContext()

        self._run_phase(
            phase=Phase.SET,
            instance=instance,
            value=value,
            ctx=ctx,
        )

        ctx.flush()

    def __delete__(self, instance: Any) -> None:
        """
        Descriptor DELETE.

        Runs Phase.DELETE within a single ExecutionContext boundary and flushes
        Timing.PHASE effects once at the end.
        """
        ctx = ExecutionContext()

        name = self._name
        current = instance.__dict__.get(name, None) if name else None

        self._run_phase(
            phase=Phase.DELETE,
            instance=instance,
            value=current,
            ctx=ctx,
        )

        ctx.flush()

    # ------------------------------------------------------------------
    # Callable semantics (Codex as Step)
    # ------------------------------------------------------------------

    def __call__(self, value: Any) -> Any:
        """
        Allow Codex to be used as a Step inside another Codex.

        Semantics
        ---------
        - Executes ONLY Phase.SET
        - Behaves as a pure transformation: value -> value
        - Uses a single ExecutionContext per call (so Timing.PHASE works)
        - Descriptor routing (instance writes) is NOT active (instance=None)
        """
        ctx = ExecutionContext()
        result = self._run_phase(
            phase=Phase.SET,
            instance=None,
            value=value,
            ctx=ctx,
        )
        ctx.flush()
        return result
