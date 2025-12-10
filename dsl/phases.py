# ================================================================
# architech/dsl/phases.py
# ================================================================
"""
PhaseToken — entrypoint into the DSL.

A PhaseToken wraps a backend-defined `DSLPhaseKey` and provides a
syntactic anchor for starting a fluent StepChain:

    SET >> f1 << fb1 >> f2 @ semantic

Backends (such as Codex) expose concrete tokens like:

    SET = PhaseToken(Phase.SET)
    GET = PhaseToken(Phase.GET)

The DSL has no knowledge of the meaning of the phase key; it simply
carries it through into Section.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .protocol import DSLPhaseKey, Step

if TYPE_CHECKING:  # avoid import cycles in type-checkers
    from .builder import StepChain  # pragma: no cover


@dataclass(frozen=True, slots=True)
class PhaseToken:
    """
    Generic phase token used by the DSL.

    Backends are expected to construct concrete instances:

        class Phase(Enum):
            SET = auto()
            GET = auto()

        SET = PhaseToken(Phase.SET)
        GET = PhaseToken(Phase.GET)
    """

    key: DSLPhaseKey

    def __rshift__(self, first: Step) -> "StepChain":
        """
        Start a new StepChain with `first` as the first PRIMARY step
        for this phase.

        Example:

            SET >> f1
        """
        # Local import to avoid circular dependency with builder.py
        from .builder import StepChain

        return StepChain(phase_token=self, first=first)
