# ================================================================
# architech/control/panopticon.py  — Model B (fast, single-context)
# ================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import os

from control.config import Principle, Praxis, Effect, SemanticInstruction
from control.capture.capture import Capture
from control.capture.config import CaptureConfig
from control.capture.context import ObservationContext
from control.capture.models import Event
from control.effect import EffectExe
from control.effect.formatter import DeferredEvents


@dataclass(slots=True)
class Panopticon:
    """
    Model B — single-phase context, semantic observation per Section
    without nested context managers.

    Usage:
        with pan as px:
            call = px.observe(principle=P, domain="User.email", stage="1")
            value = call(fn1, value)
            value = call(fn2, value)
    """

    capture: Capture
    handle_on_exit: bool = True
    use_observe_cache: bool = True

    _deferred: List[Tuple[Principle, Event]] = field(default_factory=list, init=False)
    _ctx: Optional[Any] = field(default=None, init=False)
    _ctx_logbook: Optional[Any] = field(default=None, init=False)
    _observe_cache: Dict[Tuple[Optional[Principle], str, str, bool, bool, Optional[bool]], Callable[[Callable[..., Any], Any], Any]] = field(
        default_factory=dict, init=False
    )

    # ------------------------------------------------------------
    # Context manager for whole semantic session
    # ------------------------------------------------------------
    def __enter__(self) -> "Panopticon":
        self._ctx = ObservationContext.push()
        self._ctx_logbook = self._ctx.__enter__()
        # Allow environment toggle for benchmarking: ARCHITECH_OBSERVE_CACHE=0 disables cache
        flag = os.getenv("ARCHITECH_OBSERVE_CACHE")
        if flag is not None:
            self.use_observe_cache = flag not in ("0", "false", "False")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._ctx is not None:
            self._ctx.__exit__(exc_type, exc, tb)

        if exc_type is None and self.handle_on_exit and self._deferred:
            self._handle_deferred_on_exit()

        return False

    # ------------------------------------------------------------
    # FAST observation wrapper (no nested context managers)
    # ------------------------------------------------------------
    def observe(
        self,
        principle: Optional[Principle],
        *,
        domain: str,
        stage: str,
        capture_values: bool = False,
        capture_types: bool = False,
        measure_micro_time: bool | None = None,
    ) -> Callable[[Callable[..., Any], Any], Any]:
        """
        Return a call-function that:
            - applies CaptureConfig(domain, stage, ...)
            - applies SemanticInstruction(principle)
            - delegates to Panopticon.call()
        """
        # Cache key for wrapper reuse to avoid re-allocating configs/instructions.
        cache_key = (principle, domain, stage, bool(capture_values), bool(capture_types), measure_micro_time)
        if self.use_observe_cache:
            cached = self._observe_cache.get(cache_key)
            if cached is not None:
                return cached

        # Map deprecated flags to new input/output policy model.
        input_policy = None
        output_policy = None
        if capture_values or capture_types:
            from control.capture.config import CaptureValue
            input_policy = CaptureValue(capture=capture_values, types=None)
            output_policy = CaptureValue(capture=capture_values, types=None)
        cfg = CaptureConfig(
            domain=domain,
            stage=stage,
            input=input_policy,
            output=output_policy,
            measure_micro_time=measure_micro_time,
        )
        instr = SemanticInstruction(principle=principle)

        def call(fn: Callable[..., Any], value: Any) -> Any:
            return self.call(
                fn,
                value,
                config=cfg,
                instruction=instr,
            )
        # Store in cache for reuse across steps/sections with same parameters
        if self.use_observe_cache:
            self._observe_cache[cache_key] = call
        return call

    # ------------------------------------------------------------
    # Core per-call mechanics (unchanged)
    # ------------------------------------------------------------
    def call(
        self,
        fn: Callable[..., Any],
        *args,
        config: Optional[CaptureConfig] = None,
        instruction: Optional[SemanticInstruction] = None,
        **kwargs,
    ) -> Any:
        cfg = config or CaptureConfig()
        instr = instruction or SemanticInstruction()

        effective_cfg = CaptureConfig(
            domain=cfg.domain,
            stage=cfg.stage,
            input=cfg.input,
            output=cfg.output,
            measure_micro_time=cfg.measure_micro_time,
        )

        label = instr.principle.label if instr.principle else None

        result = self.capture(
            fn,
            *args,
            config=effective_cfg,
            label=label,
            **kwargs,
        )

        lb = ObservationContext.current()
        event = lb.last()
        if not event:
            return result

        if instr.principle:
            self._apply_semantics(instr.principle, event)

        return result

    # ------------------------------------------------------------
    # Semantics
    # ------------------------------------------------------------
    def _apply_semantics(self, principle: Principle, event: Event) -> None:
        praxis = principle.praxis
        post = event.post

        if post is None:
            return

        if praxis & Praxis.IGNORE or praxis is Praxis.NONE:
            return

        if praxis & Praxis.IMMEDIATE:
            key = principle.effect.key()
            if key is not None:
                EffectExe.realize(key, [(principle, event)])
            return

        if praxis & Praxis.DEFER:
            self._deferred.append((principle, event))
            return

    # ------------------------------------------------------------
    # Deferred event flushing
    # ------------------------------------------------------------
    def _handle_deferred_on_exit(self):
        merged = self._deferred
        by_effect: Dict[Effect, List[Tuple[Principle, Event]]] = {}

        for principle, event in merged:
            by_effect.setdefault(principle.effect, []).append((principle, event))

        def pack(items):
            return items

        # 1. non-RAISE, non-NONE
        for eff, events in by_effect.items():
            if eff in (Effect.RAISE, Effect.NONE):
                continue
            key = eff.key()
            if key:
                EffectExe.realize(key, pack(events))

        # 2. RAISE last
        raise_events = by_effect.get(Effect.RAISE)
        if raise_events:
            key = Effect.RAISE.key()
            if key:
                EffectExe.realize(key, pack(raise_events))
