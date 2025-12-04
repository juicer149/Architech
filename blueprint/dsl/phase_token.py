# ================================================================
# blueprint/dsl/phase_token.py
# ================================================================
"""
Generic PhaseTokenBase used by the DSL.

Codex provides concrete SET/GET implementation by constructing
PhaseTokenBase with Codex-specific phase keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .protocol import CallableLike, DSLPhaseKey
from .syntax import StepChain


@dataclass(frozen=True, slots=True)
class PhaseTokenBase:
    """
    Phase token used by the DSL to start a Section.

    Codex will subclass or wrap this to provide named tokens like SET, GET.
    """

    phase_key: DSLPhaseKey
    phase_kwargs: Dict[str, Any]

    def with_overrides(self, **kwargs: Any) -> "PhaseTokenBase":
        """Return a new PhaseTokenBase with updated phase_kwargs."""
        merged = dict(self.phase_kwargs)
        merged.update(kwargs)
        return PhaseTokenBase(self.phase_key, merged)

    def __call__(self, **kwargs: Any) -> "PhaseTokenBase":
        """Convenience: allow SET(strict=True) style calls."""
        return self.with_overrides(**kwargs)

    def __rshift__(self, fn: CallableLike) -> StepChain:
        """Start a new StepChain with an initial primary step."""
        return StepChain(
            phase_key=self.phase_key,
            phase_kwargs=self.phase_kwargs,
            steps=[(True, fn)],
            semantic=None,
        )
