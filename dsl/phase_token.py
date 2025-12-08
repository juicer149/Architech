# ================================================================
# architech/dsl/phase_token.py
# ================================================================
"""
Generic phase token used as an entrypoint into the DSL.

A PhaseTokenBase wraps a backend-defined `DSLPhaseKey` and provides the
syntactic anchor for starting a section:

    SET >> f1 << fb1 >> f2 | semantic

Backends (such as Codex) expose concrete tokens like:

    SET = PhaseTokenBase(Phase.SET)
    GET = PhaseTokenBase(Phase.GET)

The DSL has no knowledge of the meaning of the phase key; it simply
carries it through to SectionNode.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from .protocol import DSLPhaseKey, StepFn

if TYPE_CHECKING:
    from .syntax import StepChain  # avoid import cycles


@dataclass(frozen=True, slots=True)
class PhaseTokenBase:
    """
    Generic phase token used by the DSL.
    """
    key: DSLPhaseKey

    def __rshift__(self, fn: StepFn) -> StepChain:
        """
        Start a new StepChain with `fn` as the primary step of the first cluster.
        """
        from .syntax import StepChain  # avoid import cycles
        return StepChain(phase_token=self, first=fn)

    def with_options(self, **options: Any) -> "PhaseTokenBase":
        """Attach backend-specific phase options, if desired."""
        clone = PhaseTokenBase(self.key)
        object.__setattr__(clone, "_options", dict(options))
        return clone

    @property
    def options(self) -> dict[str, Any]:
        """Return backend-provided options (if any)."""
        return getattr(self, "_options", {})
