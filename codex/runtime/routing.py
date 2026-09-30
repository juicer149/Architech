# =============================================================================
# architech/codex/runtime/routing.py
# =============================================================================
"""
DescriptorRouting — imperative execution shell for Codex.

This is the ONLY place where:
- instances are mutated
- exceptions are raised
- warnings are emitted
- Output hooks are executed
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, Optional

from ..ir.config import PhaseConfig, default_phase_config
from ..ir.effect import Effect
from ..ir.output import Output
from ..ir.phase import Phase
from ..ir.plan import PhasePlan
from .engine import Engine
from .plan import RuntimePipeline, RuntimePhasePlan
from .context import ExecutionContext


class DescriptorRouting:
    def __init__(
        self,
        plans: Dict[Phase, PhasePlan],
        overrides: Optional[Dict[Phase, PhaseConfig]] = None,
    ):
        self._plans = plans
        self._overrides = overrides or {}
        self._configs: Dict[Phase, PhaseConfig] = {}
        self._engine = Engine()
        self._name: Optional[str] = None

        self._build_configs()
        self._build_runtime_plans()

    # ------------------------------------------------------------------
    # Descriptor protocol
    # ------------------------------------------------------------------

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _build_configs(self) -> None:
        for phase, plan in self._plans.items():
            cfg = default_phase_config(phase)

            if plan.write is not None:
                cfg.write = plan.write
            if plan.exc is not None:
                cfg.exc = plan.exc

            if phase in self._overrides:
                cfg = self._overrides[phase]

            cfg.write.validate()
            cfg.exc.validate()
            self._configs[phase] = cfg

    def _build_runtime_plans(self) -> None:
        self._runtime_plans = {
            phase: RuntimePhasePlan(
                pipeline=RuntimePipeline(tuple(plan.pipeline.nodes))
            )
            for phase, plan in self._plans.items()
        }

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def _run_phase(
        self,
        *,
        phase: Phase,
        instance: Any,
        value: Any,
        ctx: ExecutionContext,
    ) -> Any:
        plan = self._runtime_plans.get(phase)
        if plan is None:
            return value if phase is Phase.GET else None

        cfg = self._configs[phase]
        field_name: str = self._name or "<unnamed>"

        # Pre-hook
        if cfg.pre is not None:
            value = cfg.pre(value, instance, field_name, phase)

        # Execute pipeline
        result, is_exc = self._engine.run(plan.pipeline, value)
        out = cfg.exc if is_exc else cfg.write

        # Record output (immediate or deferred)
        final = ctx.record(
            out=out,
            value=result,
            instance=instance,
            field_name=field_name,
            apply=self._apply_output,
        )

        # Post-hook
        if cfg.post is not None:
            cfg.post(result, instance, field_name, phase)

        return final

    # ------------------------------------------------------------------
    # Output materialization
    # ------------------------------------------------------------------

    def _apply_output(
        self,
        out: Output,
        result: Any,
        instance: Any,
        field_name: str,
    ) -> Any:
        if not out.enabled or out.effect is Effect.DROP:
            return None

        if out.effect is Effect.CUSTOM:
            assert out.hook is not None
            return out.hook(result, instance, field_name)

        if isinstance(result, BaseException):
            if out.allows_fallback:
                warnings.warn(
                    f"Codex: {field_name} produced exception {result!r}; "
                    f"using default={out.default!r}",
                    RuntimeWarning,
                    stacklevel=3,
                )
                result = out.default
            else:
                raise result

        tf = out.normalized_type_filter
        if tf is not None and not isinstance(result, tf):
            if out.allows_fallback:
                result = out.default
            else:
                raise TypeError(
                    f"Codex: {field_name} produced {type(result).__name__}, expected {tf}"
                )

        instance.__dict__[field_name] = result
        return None
