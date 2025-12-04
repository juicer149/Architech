# ================================================================
# architech/control/config.py
# ================================================================
"""
Semantic configuration types for the control layer.

This module defines:

- Praxis:
    Bit-flags that describe *when* a semantic effect should be realized
    (immediately, deferred until context exit, or ignored).

- Effect:
    Enum that describes *how* semantic events should be surfaced
    (e.g. as printed text, as an aggregated exception, etc.).

- Principle:
    A semantic rule (label + Praxis + Effect + optional exc_type)
    that can be attached to a captured call.

- SemanticInstruction:
    Wrapper passed down to Panopticon, carrying a Principle (or None).

These types form the semantic contract between the mechanical capture
layer (architech.control.capture) and higher-level constructs
such as Codex and pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntFlag, auto
from typing import Optional, Type


# ---------------------------------------------------------------------------
# Praxis — semantic timing flags
# ---------------------------------------------------------------------------


class Praxis(IntFlag):
    """
    Semantic timing flags that describe *when* to realize an Effect.

    The Praxis value of a Principle determines how Panopticon should
    schedule the Effect associated with the Event produced by the
    capture layer.

    Flags
    -----
    NONE:
        No semantic handling is applied. The Event may still live in
        the LogBook, but Panopticon does not realize any Effect for it.

    IMMEDIATE:
        Realize the Effect immediately as soon as the Event is observed.
        Typically used for interactive feedback (e.g. printing progress).

    DEFER:
        Defer realization of the Effect until the enclosing Panopticon
        context exits. Deferred events are collected and later surfaced
        in batch according to the Principle's Effect.

    IGNORE:
        Explicitly ignore the Event for semantic purposes. This is a
        stronger version of NONE when you want to document the intent.
    """

    NONE = 0
    IMMEDIATE = auto()
    DEFER = auto()
    IGNORE = auto()


# ---------------------------------------------------------------------------
# Effect — semantic enum for how events are surfaced
# ---------------------------------------------------------------------------


class Effect(Enum):
    """
    Semantic mode for *how* Events should be surfaced.

    Effect is intentionally abstract. Panopticon uses it to:

        - derive a logical key string for the EffectExe layer,
        - allow ordering decisions (e.g. realize reporting modes before
          raising an exception).

    The EffectExe layer then maps that key to concrete behavior
    (printing, raising, logging, sending emails, etc.).

    Members
    -------
    NONE:
        Do not surface the Event at all. Useful for metrics-only or
        cases where semantics only affect timing (Praxis).

    PRINT:
        Surface Events as human-readable text (e.g. CLI output).

    RAISE:
        Surface Events as an aggregated exception. Typically executed
        last so that other reporting modes have a chance to run first.

    Future extensions (examples)
    ----------------------------
    JSON, EMAIL, LOG, ... can be added later and mapped to
    a suitable logical key via `key()`.
    """

    NONE = auto()
    PRINT = auto()
    RAISE = auto()

    def key(self) -> Optional[str]:
        """
        Map this Effect to a logical outcome key string.

        This key is passed to the EffectExe layer, which maps it to a
        concrete executor (see architech.control.effect.executor).
        Panopticon does NOT interpret the meaning of this string; it only
        uses it to dispatch and to control ordering (e.g. RAISE-like
        modes last).

        Returns
        -------
        str | None
            Logical key for EffectExe (e.g. "print", "raise"), or None if
            this effect should not be surfaced at all.
        """
        match self:
            case Effect.NONE:
                return None
            case Effect.PRINT:
                return "print"
            case Effect.RAISE:
                return "raise"
            case _:
                # Future extension point for additional effects
                return self.name.lower()


# ---------------------------------------------------------------------------
# Principle — semantic rule for a captured call
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Principle:
    """
    Semantic principle applied to a captured Event.

    A Principle is the unit of semantic policy attached to a call:

        - what label to use for diagnostics,
        - when to realize the effect (Praxis),
        - how to surface it (Effect),
        - which exception type to use when raising (optional).

    Attributes
    ----------
    label:
        Human-readable label for diagnostics (e.g. "warning", "error").

    praxis:
        Praxis flags (IMMEDIATE/DEFER/IGNORE/NONE) describing when
        semantic realization should happen.

    effect:
        Effect describing how Events under this Principle should be
        surfaced (PRINT, RAISE, etc.). The timing is controlled solely
        by Praxis.

    exc_type:
        Optional exception type to use when an aggregated error is raised.
        This is consumed by higher layers:

            - Codex strict-mode:
                • may map raw errors for a section into this exception type.
            - EffectExe + Panopticon when Effect.RAISE is used:
                • may choose this type as the final raised exception.

        If exc_type is None, RuntimeError is used as the generic default.
    """

    label: str
    praxis: Praxis
    effect: Effect = Effect.RAISE
    exc_type: Optional[Type[BaseException]] = None

    def effective_exc_type(self) -> Type[BaseException]:
        """
        Return the concrete exception type to use for this Principle.

        If `exc_type` is None, RuntimeError is used as a safe default.
        """
        return self.exc_type or RuntimeError


# ---------------------------------------------------------------------------
# SemanticInstruction — container passed into Panopticon.call
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SemanticInstruction:
    """
    Instruction object used to attach semantics to a captured call.

    Higher-level systems (e.g. Codex, pipelines) construct a
    SemanticInstruction and pass it to Panopticon.call() along with
    a CaptureConfig.

    Attributes
    ----------
    principle:
        Optional Principle describing how to treat the resulting Event.
        If None, Panopticon performs no semantic handling for that call
        (it still performs mechanical capture).
    """

    principle: Optional[Principle] = None
