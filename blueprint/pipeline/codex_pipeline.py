# ================================================================
# blueprint/pipeline/codex_pipeline.py — Model B (single pan-context per Phase)
# ================================================================
"""
PipelineCompiler — compile CodexBinding into executable semantic pipelines.

Model B (Panopticon v2)
-----------------------
This compiler targets the block-oriented Panopticon API:

    with pan as px:
        call = px.observe(principle=P, domain="User.email", stage="1")
        value = call(fn1, value)
        value = call(fn2, value)

Design goals:
    • One Panopticon context per *Phase* (not per Section/Step)
    • One semantic wrapper (`observe`) per Section
    • Mechanical capture and semantic rules applied by Panopticon
    • PipelineCompiler only handles structure + Step fallback logic

Execution Modes
---------------
strict=True:
    • Direct Python calls only
    • No capture, no Panopticon, no semantics timing
    • Principles may still map exceptions via `exc_type`
    • Fastest possible mode

strict=False:
    • Fully interpreted
    • Uses Panopticon.observe() for every Section
    • Each Phase compiled into a single “mega-stage”
    • Panopticon handles capture, events, Praxis, Effect

strict=None (auto):
    • Interpreted if ANY Section uses a Principle
    • Otherwise strict

Pipeline shape
--------------
strict=True:
    Phase.SET → [stage1, stage2, ...]
    Phase.GET → [stage1, stage2, ...]

interpreted:
    Phase.SET → [single_stage_running_all_sections]
    Phase.GET → [single_stage_running_all_sections]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from control.panopticon import Panopticon
from blueprint.codex.models import Fn, Step, Section, CodexConfig, PhaseConfig, Phase
from blueprint.linker.codex_binding import CodexBinding, PhaseBinding, SectionBinding


PipelineStage = Callable[[Any], Any]
PipelineMap = Dict[Phase, List[PipelineStage]]


# ================================================================
# PipelineCompiler
# ================================================================
@dataclass
class PipelineCompiler:
    """
    Compile CodexBinding into executable pipelines (strict/interpreted).

    strict=True:
        • direct calls
        • no Panopticon
        • Principle.exc_type maps Python exceptions

    interpreted:
        • one `with pan` per Phase
        • per-Section semantics via px.observe()
        • semantics (Praxis/Effect) applied correctly

    This compiler contains *no semantic logic* itself; it delegates
    all semantics to Panopticon.call() and Panopticon.observe().
    """

    # ------------------------------------------------------------
    # Top-level: build full pipeline map
    # ------------------------------------------------------------
    def build_pipeline(
        self,
        *,
        binding: CodexBinding,
        panopticon: Panopticon | None,
    ) -> PipelineMap:

        has_semantics_global = self._has_semantics(binding)
        pipelines: PipelineMap = {}

        for phase_binding in binding:
            eff_strict = self._resolve_strict_for_phase(
                codex_cfg=binding.config,
                phase_cfg=phase_binding.config,
                has_semantics_global=has_semantics_global,
                phase_binding=phase_binding,
            )

            # STRICT MODE: each Section is compiled independently
            if eff_strict:
                stages = [
                    self._compile_strict(sec_binding)
                    for sec_binding in phase_binding
                ]
                if stages:
                    pipelines[phase_binding.phase] = stages
                continue

            # INTERPRETED MODE: one “mega-stage” per Phase
            if panopticon is None:
                raise RuntimeError(
                    "Interpreted mode requested but no Panopticon was provided."
                )

            stage = self._compile_interpreted_phase(
                binding=binding,
                phase_binding=phase_binding,
                pan=panopticon,
            )
            pipelines[phase_binding.phase] = [stage]

        return pipelines

    # ------------------------------------------------------------
    # Semantics detection helpers
    # ------------------------------------------------------------
    @staticmethod
    def _has_semantics(binding: CodexBinding) -> bool:
        return any(
            sb.principle is not None
            for phase in binding.phases
            for sb in phase.sections
        )

    @staticmethod
    def _has_semantics_phase(phase_binding: PhaseBinding) -> bool:
        return any(sb.principle is not None for sb in phase_binding.sections)

    def _resolve_strict_for_phase(
        self,
        *,
        codex_cfg: CodexConfig,
        phase_cfg: PhaseConfig,
        has_semantics_global: bool,
        phase_binding: PhaseBinding,
    ) -> bool:

        # 1. Phase-level override
        if phase_cfg.strict is not None:
            return phase_cfg.strict

        # 2. Codex-level override
        if codex_cfg.strict is not None:
            return codex_cfg.strict

        # 3. Auto: if any principle → interpreted
        return not (has_semantics_global or self._has_semantics_phase(phase_binding))

    # ------------------------------------------------------------
    # STRICT MODE
    # ------------------------------------------------------------
    def _compile_strict(self, sec_binding: SectionBinding) -> PipelineStage:
        """
        strict=True:
            • direct Python calls
            • no capture, no semantics, no events
            • soft-error convention (fn returns Exception → raise it)
            • Principle.exc_type may map raised errors
        """
        section = sec_binding.section
        principle = sec_binding.principle

        def call(fn: Fn, value: Any) -> Any:
            result = fn(value)
            if isinstance(result, BaseException):
                raise result
            return result

        runner = self._build_runner(section, call)

        if principle is None:
            return runner

        exc_type = getattr(principle, "exc_type", None)
        if exc_type is None:
            return runner

        def stage(value: Any) -> Any:
            try:
                return runner(value)
            except BaseException as err:
                if isinstance(err, exc_type):
                    raise
                raise exc_type(str(err)) from err

        return stage

    # ------------------------------------------------------------
    # INTERPRETED MODE (Model B: one pan-context per Phase)
    # ------------------------------------------------------------
    def _compile_interpreted_phase(
        self,
        *,
        binding: CodexBinding,
        phase_binding: PhaseBinding,
        pan: Panopticon,
    ) -> PipelineStage:
        """
        Interpreted execution:
            • one `with pan` per Phase
            • each Section gets its own call-wrapper from px.observe()
            • each Step runs through that wrapper
        """

        domain = binding.domain
        sections = tuple(phase_binding.sections)

        def stage(value: Any) -> Any:
            if not sections:
                return value

            with pan as px:
                cur = value
                for sec_binding in sections:
                    principle = sec_binding.principle
                    stage_id = sec_binding.id
                    phase_cfg = phase_binding.config

                    # px.observe binds Principle + (domain, stage)
                    # Request minimal capture so Events are produced
                    # and effects (e.g., PRINT) can surface diagnostics.
                    call = px.observe(
                        principle=principle,
                        domain=domain,
                        stage=stage_id,
                        capture_values=bool(getattr(phase_cfg, "capture_values", True)),
                        capture_types=False,
                    )
                    # Raw direct call for fallback probing (no capture/semantics)
                    def call_raw(fn: Fn, val: Any) -> Any:
                        res = fn(val)
                        if isinstance(res, BaseException):
                            raise res
                        return res

                    section = sec_binding.section
                    for step in section.steps:
                        probe_mode = getattr(phase_cfg, "probe_capture", "none")
                        cur = self._run_step(step, cur, call, call_raw if probe_mode == "none" else None)

                return cur

        return stage

    # ------------------------------------------------------------
    # Step runner (fallback cascade)
    # ------------------------------------------------------------
    @staticmethod
    def _run_step(step: Step, value: Any, call: Callable[[Fn, Any], Any], call_raw: Callable[[Fn, Any], Any] | None = None) -> Any:
        try:
            return call(step.fn, value)
        except BaseException as primary_error:
            last = primary_error
            cur = value

            for fb in step.fallbacks:
                try:
                    # Prefer raw probe without capture if available
                    if call_raw is not None:
                        cur = call_raw(fb, cur)
                    else:
                        cur = call(fb, cur)
                    return call(step.fn, cur)
                except BaseException as e:
                    last = e

            raise last

    # ------------------------------------------------------------
    # Section runner builder (strict mode)
    # ------------------------------------------------------------
    def _build_runner(
        self,
        section: Section,
        call: Callable[[Fn, Any], Any],
    ) -> PipelineStage:

        _run_step = self._run_step
        steps = section.steps

        def run(value: Any) -> Any:
            cur = value
            for step in steps:
                cur = _run_step(step, cur, call)
            return cur

        return run
