"""
architech.loader.source.python
------------------------------
Deterministic backend for loading Python modules and class-based entities.

───────────────────────────────────────────────────────────────────────────────
Purpose
───────────────────────────────────────────────────────────────────────────────
This backend implements the *Python-specialized realization* of the deterministic
loading contract defined in `architech.loader.base.BaseLoader`.

It provides a complete, multi-phase lifecycle for discovering, importing, and
instantiating Python-based entities — in a deterministic, cache-backed, and
reflection-safe manner.

───────────────────────────────────────────────────────────────────────────────
Deterministic Lifecycle
───────────────────────────────────────────────────────────────────────────────
This backend concretizes the abstract three-phase contract:

    1️⃣ `_build_static(path)`  
        - Fastest path, uses in-memory registry lookup.
        - Avoids imports entirely when the class is already registered.
        - Typically used by bootstrapped systems or pre-loaded subsystems.

    2️⃣ `try_resolve(path)`  
        - Intermediate deterministic import phase.
        - Imports a module directly (no reflection) and looks for a known `entry_name`.
        - Ideal for systems where entity naming follows convention (e.g., class Argon2 in argon2.py).

    3️⃣ `_build_dynamic(path)`  
        - Reflective fallback phase.
        - Introspects all classes in a module deterministically and instantiates the first eligible one.
        - Used when no explicit registry entry or entry_name is defined.

Each phase yields a `DiagnosticReport`, ensuring full traceability.

───────────────────────────────────────────────────────────────────────────────
Design Highlights
───────────────────────────────────────────────────────────────────────────────
• Deterministic import via `importlib.import_module`  
• Zero mutable global state — caching handled at class-level via `lru_cache`  
• Orthogonal contract filtering using `base_contract`  
• Full compatibility with Architech’s diagnostic and registry subsystems  
• Predictable failure behavior (strict vs. non-strict mode)

───────────────────────────────────────────────────────────────────────────────
Example
───────────────────────────────────────────────────────────────────────────────
    from architech.loader.source.python import Python

    loader = Python(registry={"argon2": Argon2})
    report, instance = loader.load(("securitykit", "hashing", "algorithm", "argon2"))

    print(report.summary())
    # securitykit.hashing.algorithm.argon2: ok
───────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import importlib
import inspect
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

from loader.base import BaseLoader, StaticLoadError, DynamicLoadError
from observation.report import DiagnosticReport


# ============================================================================
# PYTHON LOADER
# ============================================================================
class Python(BaseLoader):
    """
    Deterministic loader for Python-based modules and class entities.

    Implements:
        - Registry-based instantiation (static phase)
        - Deterministic import via `importlib` (resolve phase)
        - Reflective fallback with `inspect` (dynamic phase)

    All operations are cache-backed, deterministic, and produce structured
    diagnostics.
    """

    # ----------------------------------------------------------------------
    # Shared deterministic caches
    # ----------------------------------------------------------------------
    _module_cache: Dict[str, Any] = {}
    _class_cache: Dict[str, Tuple[type, ...]] = {}

    # ----------------------------------------------------------------------
    # Path normalization
    # ----------------------------------------------------------------------
    @classmethod
    def normalize_path(cls, path: str | tuple[str, ...]) -> str:
        """
        Normalize input into canonical import path.

        Examples:
            ("a", "b", "c")  → "a.b.c"
            "a/b/c.py"       → "a.b.c"
            "a.b.c"          → "a.b.c"
        """
        if isinstance(path, tuple):
            path = ".".join(path)
        p = path.replace("\\", "/").strip().strip("/")
        if p.endswith(".py"):
            p = p[:-3]
        return p.replace("/", ".")

    # ----------------------------------------------------------------------
    # Phase 1 — Static registry lookup
    # ----------------------------------------------------------------------
    def _build_static(
        self, path: str | tuple[str, ...], **kwargs: Any
    ) -> Tuple[DiagnosticReport, Optional[Any]]:
        """
        Attempt deterministic instantiation from in-memory registry.

        Fastest path — no imports or reflection. Used primarily when the
        system has already registered the class in `self.registry`.

        Example:
            >>> self.registry = {"argon2": Argon2}
            >>> report, obj = self._build_static("securitykit.hashing.algorithm.argon2")
        """
        identifier = self.normalize_path(path).split(".")[-1]
        cls = self.registry.get(identifier)

        if not cls:
            msg = f"No registry entry for '{identifier}'"
            return DiagnosticReport(identifier, info=(msg,)), None

        try:
            instance = cls(**(kwargs.get("init_kwargs") or {}))
            return DiagnosticReport(identifier, info=(f"Loaded '{identifier}' from registry",)), instance
        except Exception as e:
            msg = f"Static instantiation failed for '{identifier}': {e}"
            if self.strict_mode:
                raise StaticLoadError(msg)
            return DiagnosticReport(identifier, errors=(msg,)), None

    # ----------------------------------------------------------------------
    # Phase 2 — Deterministic import (no reflection)
    # ----------------------------------------------------------------------
    def try_resolve(
        self, path: str | tuple[str, ...], **kwargs: Any
    ) -> Tuple[DiagnosticReport, Optional[Any]]:
        """
        Deterministically import the module and instantiate a known entry name.

        If `self.entry_name` is defined and the module exports a class with that
        name, it is instantiated directly — no reflection required.
        """
        module_path = self.normalize_path(path)
        if self.variant_suffix:
            module_path = f"{module_path}.{self.variant_suffix}"

        try:
            module = self._import_module_cached(module_path)
            entry_name = getattr(self, "entry_name", None)

            if entry_name and hasattr(module, entry_name):
                cls = getattr(module, entry_name)
                instance = cls(**(kwargs.get("init_kwargs") or {}))
                info = f"Resolved deterministically via '{module_path}.{entry_name}'"
                return DiagnosticReport(module_path, info=(info,)), instance

            info = f"Module '{module_path}' importable but no matching entry found"
            return DiagnosticReport(module_path, info=(info,)), None

        except ModuleNotFoundError:
            msg = f"Module not found during resolve: {module_path}"
            return DiagnosticReport(module_path, errors=(msg,)), None

        except Exception as e:
            msg = f"Deterministic import failed for {module_path}: {e}"
            return DiagnosticReport(module_path, warnings=(msg,)), None

    # ----------------------------------------------------------------------
    # Phase 3 — Dynamic reflection fallback
    # ----------------------------------------------------------------------
    def _build_dynamic(
        self, path: str | tuple[str, ...], **kwargs: Any
    ) -> Tuple[DiagnosticReport, Optional[Any]]:
        """
        Reflectively discover and instantiate a class from a Python module.

        If no explicit entry_name or registry entry exists, this phase enumerates
        all classes defined in the module (via `inspect.getmembers`) and selects
        the first that matches the `base_contract` (if provided).

        Reflective fallback — slower but fully deterministic.
        """
        module_path = self.normalize_path(path)
        if self.variant_suffix:
            module_path = f"{module_path}.{self.variant_suffix}"

        try:
            module = self._import_module_cached(module_path)
            candidates = self._get_eligible_classes(module)

            if not candidates:
                msg = f"No eligible classes found in {module_path}"
                return DiagnosticReport(module_path, warnings=(msg,)), None

            selected = candidates[0]
            instance = selected(**(kwargs.get("init_kwargs") or {}))
            info = f"Instantiated {selected.__name__} from {module_path}"
            return DiagnosticReport(module_path, info=(info,)), instance

        except Exception as e:
            msg = f"Dynamic import failed for {module_path}: {e}"
            if self.strict_mode:
                raise DynamicLoadError(msg)
            return DiagnosticReport(module_path, errors=(msg,)), None

    # ----------------------------------------------------------------------
    # Deterministic caching layers
    # ----------------------------------------------------------------------
    @classmethod
    @lru_cache(maxsize=128)
    def _import_module_cached(cls, module_path: str) -> Any:
        """
        Deterministically import and cache a Python module.

        Caching ensures that repeated lookups of the same module are O(1)
        after first import. Thread-safe via class-level cache.
        """
        if module_path in cls._module_cache:
            return cls._module_cache[module_path]
        module = importlib.import_module(module_path)
        cls._module_cache[module_path] = module
        return module

    @classmethod
    @lru_cache(maxsize=128)
    def _get_classes_from_module(cls, module: Any) -> Tuple[type, ...]:
        """
        Return all defined classes within a module deterministically.
        Results are cached by module name for fast repeated lookups.
        """
        name = module.__name__
        if name in cls._class_cache:
            return cls._class_cache[name]
        classes = tuple(c for _, c in inspect.getmembers(module, inspect.isclass))
        cls._class_cache[name] = classes
        return classes

    # ----------------------------------------------------------------------
    # Reflection utilities
    # ----------------------------------------------------------------------
    def _get_eligible_classes(self, module: Any) -> list[type]:
        """
        Return deterministic list of eligible class candidates.

        If `base_contract` is set, filters out non-conforming classes.
        Otherwise, returns all defined classes in declaration order.
        """
        all_classes = list(self._get_classes_from_module(module))
        if self.base_contract:
            return [
                c for c in all_classes
                if issubclass(c, self.base_contract) and c is not self.base_contract
            ]
        return all_classes

    # ----------------------------------------------------------------------
    # Representation
    # ----------------------------------------------------------------------
    def __repr__(self) -> str:
        contract = getattr(self.base_contract, "__name__", None)
        return f"<PythonLoader contract={contract} registry={len(self.registry)}>"
