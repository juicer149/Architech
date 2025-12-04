"""
architech.loader.engine
-----------------------
EntityConstructor — deterministic, source-agnostic orchestrator.

───────────────────────────────────────────────────────────────────────────────
Purpose
───────────────────────────────────────────────────────────────────────────────
Defines the *deterministic orchestration layer* connecting declarative
specifications (what to load and where it lives) with concrete loader
backends (Python, JSON, YAML, ENV, etc.).

It defines three complementary abstractions:

    • EntityLocator     — declarative descriptor of *what and where*  
    • EntityContext     — runtime descriptor of *how*  
    • EntityConstructor — deterministic orchestrator delegating to loaders  

───────────────────────────────────────────────────────────────────────────────
Design Philosophy
───────────────────────────────────────────────────────────────────────────────
• Declarative separation — Locator (what/where) ≠ Context (how)  
• Backend determinism — each backend resolves its own path, extension, and logic  
• Liberal in input — accepts strings, tuples, or Paths; normalizes early  
• Conservative in output — always produces deterministic tuple-based paths  
• No silent failures — all outcomes yield a DiagnosticReport  
• Fully composable — every part reusable in isolation or chains  

───────────────────────────────────────────────────────────────────────────────
Example
───────────────────────────────────────────────────────────────────────────────
    from architech.loader.engine import EntityLocator, EntityContext, EntityConstructor
    from securitykit.hashing.algorithm import Argon2, Bcrypt

    locator = EntityLocator(
        base="securitykit.hashing.algorithm",
        filename="argon2",
        source="python",
    )

    context = EntityContext(
        registries={
            "securitykit.hashing.algorithm": {
                "registry": {"argon2": Argon2, "bcrypt": Bcrypt}
            }
        },
        strict_mode=False,
    )

    report, entity = EntityConstructor().load(locator, context)
    print(report.summary())
───────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, Type, Union

from loader.source import resolve_backend, BackendResolutionError
from loader.base import BaseLoader
from observation.report import DiagnosticReport


# ============================================================================
# EntityLocator — declarative descriptor (WHAT + WHERE)
# ============================================================================
@dataclass(frozen=True, slots=True, kw_only=True)
class EntityLocator:
    """
    Immutable declarative descriptor defining *what* to load and *where* it lives.
    """

    base: str
    filename: Optional[str] = None
    entry_name: Optional[str] = None
    source: str = "python"
    variant_suffix: Optional[str] = None
    base_contract: Optional[type] = None

    # ----------------------------------------------------------------------
    # Canonical path accessors
    # ----------------------------------------------------------------------
    @property
    def module_path(self) -> str:
        """Canonical dotted import path (used for import-based backends)."""
        parts = [self.base, self.filename]
        return ".".join(p for p in parts if p)

    @property
    def path_parts(self) -> tuple[str, ...]:
        """Canonical tuple of hierarchical path components."""
        parts = self.base.split(".")
        if self.filename:
            parts.append(self.filename)
        return tuple(parts)

    # ----------------------------------------------------------------------
    # Convenience utilities
    # ----------------------------------------------------------------------
    def describe(self) -> str:
        """Compact string representation for diagnostics."""
        return f"<EntityLocator base={self.base!r} file={self.filename!r} source={self.source!r}>"

    def derive(self, **updates: Any) -> EntityLocator:
        """Return a shallow copy with updated fields (preserving immutability)."""
        data = {**self.__dict__, **updates}
        return EntityLocator(**data)  # type: ignore[arg-type]

    def with_filename(self, filename: str, *, entry_name: Optional[str] = None) -> EntityLocator:
        """Return a locator with a derived entry name (TitleCase if unspecified)."""
        entry_name = entry_name or "".join(s.capitalize() for s in filename.split("_"))
        return self.derive(filename=filename, entry_name=entry_name)


# ============================================================================
# EntityContext — runtime configuration (HOW)
# ============================================================================
@dataclass(slots=True, kw_only=True)
class EntityContext:
    """
    Runtime configuration describing *how* deterministic loading should occur.
    """

    registries: Optional[Dict[str, Any]] = None
    strict_mode: bool = False
    diagnostics_cls: Optional[Any] = None
    base_contract: Optional[type] = None
    defaults: Dict[str, Any] = field(default_factory=dict)

    def get_registry(self, owner: Optional[str]) -> Dict[str, Any]:
        """Return deterministic registry mapping for a given domain owner."""
        if not self.registries:
            return {}
        if not owner:
            return self.registries.get("registry", {})
        spec = self.registries.get(owner)
        if not spec:
            return {}
        return spec["registry"] if isinstance(spec, dict) and "registry" in spec else spec

    @property
    def is_strict(self) -> bool:
        """True if strict mode is enabled."""
        return bool(self.strict_mode)


# ============================================================================
# Path normalization helper — "liberal in, deterministic out"
# ============================================================================
def normalize_locator_path(value: Union[str, tuple[str, ...]]) -> tuple[str, ...]:
    """
    Normalize arbitrary user input into a canonical tuple representation.

    Accepts:
        "a.b.c" → ("a", "b", "c")
        "a/b/c.py" → ("a", "b", "c")
        ("a", "b", "c") → ("a", "b", "c")
    """
    if isinstance(value, tuple):
        return value
    if isinstance(value, str):
        value = value.replace("\\", "/").replace("/", ".").strip(".")
        return tuple(value.split("."))
    raise TypeError(f"Unsupported path type for normalization: {type(value)}")


# ============================================================================
# EntityConstructor — deterministic orchestrator
# ============================================================================
class EntityConstructor:
    """
    Deterministic orchestrator bridging declarative locators with concrete backends.

    Responsibilities:
        • Resolve the correct backend via `resolve_backend`
        • Configure backend with registries and context
        • Normalize locator path deterministically
        • Delegate multi-phase load to backend
        • Return merged DiagnosticReport and entity
    """

    def load(
        self,
        locator: EntityLocator,
        context: Optional[EntityContext] = None,
        *,
        filename: Optional[str] = None,
        init_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Tuple[DiagnosticReport, Optional[Any]]:
        """
        Deterministically load an entity using a locator + context pair.

        Returns:
            (DiagnosticReport, instance | None)
        """
        context = context or EntityContext()

        # 1️⃣ Inject filename if provided
        if filename and not locator.filename:
            locator = locator.with_filename(filename)

        # 2️⃣ Resolve backend class deterministically
        try:
            backend_cls: Optional[Type[BaseLoader]] = resolve_backend(locator.source)
        except BackendResolutionError as e:
            msg = f"Backend resolution failed: {e.message}"
            return DiagnosticReport.from_message("EntityConstructor", msg, level="error"), None

        if backend_cls is None:
            msg = f"No backend class resolved for source '{locator.source}'"
            return DiagnosticReport.from_message("EntityConstructor", msg, level="error"), None

        if not issubclass(backend_cls, BaseLoader):
            msg = f"Resolved backend {backend_cls.__name__} is not a subclass of BaseLoader"
            return DiagnosticReport.from_message("EntityConstructor", msg, level="error"), None

        # 3️⃣ Configure backend with context
        registry = context.get_registry(locator.base)
        backend = backend_cls(registry=registry, **context.defaults)
        backend.strict_mode = context.strict_mode
        backend.diagnostics_cls = context.diagnostics_cls
        backend.base_contract = locator.base_contract or context.base_contract
        backend.entry_name = locator.entry_name
        backend.variant_suffix = locator.variant_suffix

        # 4️⃣ Normalize path deterministically
        path_tuple = normalize_locator_path(locator.path_parts)

        # 5️⃣ Delegate deterministic load lifecycle
        try:
            report, entity = backend.load(path_tuple, init_kwargs=init_kwargs)
        except Exception as e:
            msg = f"Backend load failed for {locator.describe()}: {e}"
            if context.is_strict:
                raise
            return DiagnosticReport.from_message("EntityConstructor", msg, level="error"), None

        # 6️⃣ Return unified result
        return (report or DiagnosticReport.OK_REPORT), entity

    # ----------------------------------------------------------------------
    # Representation
    # ----------------------------------------------------------------------
    def __repr__(self) -> str:
        return "<EntityConstructor deterministic, backend-first>"
