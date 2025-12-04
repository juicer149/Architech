"""
architech.loader.source
-----------------------
Unified backend resolver for all Architech loaders.

Dynamically (yet deterministically) resolves a backend loader class given
a logical `source` identifier such as "python", "json", or "yaml".

───────────────────────────────────────────────────────────────────────────────
Philosophy
───────────────────────────────────────────────────────────────────────────────
• No hardcoded branching — resolution via import + reflection
• Deterministic import paths: architech.loader.source.{source}
• Zero mutable state, zero registration
• Explicit, composable, backend-agnostic design
───────────────────────────────────────────────────────────────────────────────
Example
───────────────────────────────────────────────────────────────────────────────
    from architech.loader.source import resolve_backend

    backend_cls = resolve_backend("python")
    loader = backend_cls(strict_mode=True)
    report, entity = loader.load("securitykit.hashing.algorithm.argon2")
───────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
import importlib
from typing import Optional, Type, Any

# ============================================================================
# Module constants
# ============================================================================
MODULE_PATH_TEMPLATE = "loader.source.{source}"

# ============================================================================
# Exceptions
# ============================================================================
class BackendResolutionError(ImportError):
    """Raised when a backend cannot be resolved deterministically."""

    def __init__(self, source: str, message: str) -> None:
        super().__init__(f"[BackendResolutionError] {message} (source='{source}')")
        self.source = source
        self.message = message


# ============================================================================
# Deterministic backend resolver
# ============================================================================
def resolve_backend(source: str) -> Optional[Type[Any]]:
    """
    Resolve a backend loader class deterministically based on source name.

    Expected module path:
        loader.source.{source}

    Expected class name (by convention):
        {Source.title()}

    Example:
        source="python" → from architech.loader.source.python import Python

    Returns:
        Loader class, or None if not implemented.
    """
    src = source.lower().strip()
    module_path = MODULE_PATH_TEMPLATE.format(source=src)
    class_name = src.capitalize()

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise BackendResolutionError(src, f"Backend module not found: {module_path}") from e

    try:
        backend_cls = getattr(module, class_name)
    except AttributeError as e:
        raise BackendResolutionError(src, f"Backend class '{class_name}' missing in module.") from e

    if not isinstance(backend_cls, type):
        raise BackendResolutionError(src, f"Resolved object '{class_name}' is not a class.")

    return backend_cls


__all__ = ["resolve_backend", "BackendResolutionError"]
