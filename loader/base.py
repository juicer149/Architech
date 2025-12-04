"""
architech.loader.base
---------------------
Deterministic abstract foundation for all Architech loader backends.

───────────────────────────────────────────────────────────────────────────────
Purpose
───────────────────────────────────────────────────────────────────────────────
Defines the **core deterministic loading contract** shared across
all loaders in the Architech system. Ensures that every loader —
whether Python, JSON, YAML, or ENV — behaves in a predictable,
traceable, and reportable way.

───────────────────────────────────────────────────────────────────────────────
Design Rationale
───────────────────────────────────────────────────────────────────────────────
Each loader follows a *multi-phase deterministic lifecycle*:

    1️⃣ `_build_static(path)`  — Registry or cache lookup  
    2️⃣ `try_resolve(path)`    — Optional deterministic resolution  
    3️⃣ `_build_dynamic(path)` — Fallback reflection or I/O resolution  

Subclasses must implement `_build_static()` and `_build_dynamic()`.
`try_resolve()` is optional but used where deterministic resolution is possible.

The base class also handles:
    • Contract validation
    • Registry enrichment (thread-safe async)
    • Unified diagnostic reporting (no silent failures)

───────────────────────────────────────────────────────────────────────────────
Integration
───────────────────────────────────────────────────────────────────────────────
The `BaseLoader` is subclassed by source-specific loaders and invoked indirectly
via `EntityConstructor`.

Example:

    from architech.loader.engine import EntityConstructor, EntityLocator, EntityContext
    from securitykit.hashing.algorithm import Argon2

    locator = EntityLocator(base="securitykit.hashing.algorithm", filename="argon2")
    context = EntityContext(registries={"securitykit.hashing.algorithm": {"registry": {"argon2": Argon2}}})

    report, instance = EntityConstructor().load(locator, context)
───────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Type, Callable, Union
from observation.report import DiagnosticReport


# ============================================================================
# Exception Hierarchy
# ============================================================================
class LoaderError(RuntimeError):
    """Base class for all deterministic loader errors."""


class StaticLoadError(LoaderError):
    """Raised when static registry-based loading fails."""


class DynamicLoadError(LoaderError):
    """Raised when reflection-based dynamic loading fails."""


# ============================================================================
# BaseLoader — unified deterministic contract
# ============================================================================
class BaseLoader(ABC):
    """
    Deterministic abstract base for all Architech loaders.

    Lifecycle (default phases):
        static → resolve → dynamic

    Control flow is deterministic and phase-driven, ensuring predictable
    load order and composable extension in future backends.
    """

    registry: Dict[str, Type[Any]]
    strict_mode: bool
    fallback_for_missing_registry: bool
    variant_suffix: Optional[str]
    diagnostic_cls: Optional[Any] = None
    entry_name: Optional[str] = None
    base_contract: Optional[Any]
    phases: tuple[str, ...] = ("static", "resolve", "dynamic")

    _registry_lock = threading.Lock()

    # ----------------------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *,
        registry: Optional[Dict[str, Type[Any]]] = None,
        strict_mode: bool = False,
        base_contract: Optional[Any] = None,
        fallback_for_missing_registry: bool = True,
        variant_suffix: Optional[str] = None,
        **config: Any,
    ) -> None:
        self.registry = registry or {}
        self.strict_mode = strict_mode
        self.base_contract = base_contract
        self.fallback_for_missing_registry = fallback_for_missing_registry
        self.variant_suffix = variant_suffix

        # Allow subclasses to attach arbitrary config
        for key, value in config.items():
            setattr(self, key, value)

    # ----------------------------------------------------------------------
    # Deterministic load orchestration
    # ----------------------------------------------------------------------
    def load(self, path: Union[str, tuple[str, ...]], **kwargs: Any) -> Tuple[DiagnosticReport, Optional[Any]]:
        """
        Deterministically load and optionally instantiate an object from a path.

        Each loader executes its defined phases in order:
            static → resolve → dynamic

        Returns:
            (DiagnosticReport, instance)
        """
        reports: list[DiagnosticReport] = []
        instance: Optional[Any] = None

        for phase_name in self.phases:
            fn = getattr(self, f"_build_{phase_name}" if phase_name != "resolve" else "try_resolve")

            report, instance = self._run_phase(phase_name, fn, path, **kwargs)

            # Append only meaningful reports (truthy ones)
            if report:
                reports.append(report)

            # Early success termination
            if instance:
                return DiagnosticReport.merge(list(reports), identifier=self.__class__.__name__), instance

            # Respect static fallback policy
            if phase_name == "static" and not self.fallback_for_missing_registry:
                return DiagnosticReport.merge(list(reports), identifier=self.__class__.__name__), None

        # No phase succeeded — return merged diagnostics (or OK if all empty)
        if not reports:
            return DiagnosticReport.OK_REPORT, None
        return DiagnosticReport.merge(list(reports), identifier=self.__class__.__name__), None

    # ----------------------------------------------------------------------
    # Internal phase executor
    # ----------------------------------------------------------------------
    def _run_phase(
        self,
        name: str,
        fn: Callable[..., Tuple[DiagnosticReport, Optional[Any]]],
        path: Union[str, tuple[str, ...]],
        **kwargs: Any,
    ) -> Tuple[DiagnosticReport, Optional[Any]]:
        """Execute a single deterministic phase safely with validation."""
        try:
            report, instance = fn(path, **kwargs)
        except Exception as e:
            msg = f"{name.title()} phase failed for {path}: {e}"
            if self.strict_mode:
                raise
            return DiagnosticReport.from_message(self.__class__.__name__, msg, level="error"), None

        # Handle successful instance
        if instance:
            validation = self._validate_instance(instance)
            merged = DiagnosticReport.merge([report, validation])
            if name in {"resolve", "dynamic"}:
                self._background_registry_update(path, instance)
            return merged, instance

        # Ensure a meaningful report exists
        if not report:
            report = DiagnosticReport.OK_REPORT
        return report, None

    # ----------------------------------------------------------------------
    # Abstract hooks
    # ----------------------------------------------------------------------
    @abstractmethod
    def _build_static(self, path: Any, **kwargs: Any) -> Tuple[DiagnosticReport, Optional[Any]]:
        """Deterministic static resolution (registry, cache, or alias)."""
        raise NotImplementedError

    @abstractmethod
    def _build_dynamic(self, path: Any, **kwargs: Any) -> Tuple[DiagnosticReport, Optional[Any]]:
        """Dynamic fallback (reflection, import, or parsing)."""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # Optional deterministic resolver
    # ----------------------------------------------------------------------
    def try_resolve(self, path: Union[str, tuple[str, ...]], **kwargs: Any) -> Tuple[DiagnosticReport, Optional[Any]]:
        """
        Optional deterministic resolution between static and dynamic.
        Backends can override this to implement predictable logic.
        """
        msg = f"Deterministic resolve not implemented for '{self.__class__.__name__}'"
        return DiagnosticReport.from_message(self.__class__.__name__, msg, level="info"), None

    # ----------------------------------------------------------------------
    # Validation
    # ----------------------------------------------------------------------
    def _validate_instance(self, instance: Any) -> DiagnosticReport:
        """Validate instance against the base_contract (if defined)."""
        if not self.base_contract:
            return DiagnosticReport.OK_REPORT
        if not isinstance(instance, self.base_contract):
            msg = f"{instance.__class__.__name__} does not implement {self.base_contract.__name__}"
            return DiagnosticReport.from_message(self.__class__.__name__, msg, level="warning")
        return DiagnosticReport.from_message(self.__class__.__name__, "Contract validation passed", level="info")

    # ----------------------------------------------------------------------
    # Registry enrichment (background-safe)
    # ----------------------------------------------------------------------
    def _background_registry_update(self, path: Union[str, tuple[str, ...]], instance: Any) -> None:
        """Enrich registry asynchronously for future fast static lookups."""
        def task() -> None:
            identifier = path[-1] if isinstance(path, tuple) else str(path).split(".")[-1]
            with self._registry_lock:
                if identifier not in self.registry:
                    self.registry[identifier] = type(instance)
                    self._debug_log(f"Registry enriched with {identifier} → {type(instance).__name__}")

        threading.Thread(
            target=task,
            name=f"{self.__class__.__name__}RegistryUpdater",
            daemon=True,
        ).start()

    # ----------------------------------------------------------------------
    # Utility methods
    # ----------------------------------------------------------------------
    @classmethod
    def normalize_path(cls, path: Union[str, tuple[str, ...]]) -> str:
        """Default path normalization; subclasses may override."""
        if isinstance(path, tuple):
            return ".".join(path)
        return path

    def _debug_log(self, msg: str) -> None:
        import os
        if os.environ.get("ARCHITECH_DEBUG_LOADER"):
            print(f"[{self.__class__.__name__}] {msg}")

    def __repr__(self) -> str:
        reg_size = len(self.registry)
        contract_name = getattr(self.base_contract, "__name__", None)
        return f"<{self.__class__.__name__} registry={reg_size} contract={contract_name}>"
