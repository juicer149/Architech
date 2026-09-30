# =============================================================================
# architech/codex/ir/contract.py
# =============================================================================
"""
Codex IR Contract.

Defines what the Codex backend expects from DSL values.
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class CodexIRContract:
    """
    Defines backend-specific constraints for Codex IR.
    """
    step_predicate: Callable[[Any], bool]


# Default Codex contract:
# Steps must be callable (functions, lambdas, Codex itself, etc.)
CODEX_CONTRACT = CodexIRContract(
    step_predicate=callable,
)
