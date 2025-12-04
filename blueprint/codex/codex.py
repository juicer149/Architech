# ================================================================
# blueprint/codex/codex.py
# ================================================================
"""
Codex — Declarative semantic pipeline descriptor.

High-level idea
---------------

Codex is a *descriptor* that attaches a semantic pipeline to a class
attribute. On assignment:

    instance.field = value

the Codex descriptor:

    - builds (or reuses) a compiled pipeline,
    - runs `value` through all SET Sections / Steps,
    - stores the internal value on the instance.

On access:

    instance.field

the Codex descriptor:

    - retrieves the stored internal value,
    - runs it through GET Sections / Steps (if any),
    - returns the transformed value.

Execution modes
---------------

strict=True:
    - Pure direct calls, no Panopticon, no semantics timing.
    - Principles may still specify `exc_type` for remapping exceptions.

strict=False:
    - Fully interpreted mode.
    - Panopticon is *required*.
    - All functions executed via Panopticon.call(...).

strict=None:
    - Automatic:
        • If ANY Section uses semantics → interpreted mode.
        • Otherwise → strict (direct calls).

Panopticon
----------

Codex does not allocate a Panopticon itself. It expects a default
Panopticon to be supplied by the control layer, e.g. in
`control.defaults.DEFAULT_PANOPTICON`. If interpreted mode is required
for a Codex instance and no explicit panopticon was provided, the
descriptor will fall back to that default.

Codex surface
-------------

    from blueprint.codex import Codex, SET, GET
    from blueprint.codex import ERROR, WARN

    class Email:
        address = Codex[
            SET >> to_str >> strip >> require_at | ERROR,
            GET >> lowercase | WARN,
        ]

Or using per-phase strict:

    class Email:
        address = Codex[
            SET(strict=True) >> normalize >> validate | ERROR,
            GET(strict=False) >> mask | WARN,
        ]

And using the explicit constructor:

    email = Codex(
        SET >> to_str >> strip,
        SET >> require_at | ERROR,
        GET >> mask_domain | WARN,
        strict=None,
        panopticon=None,
        default=None,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, Type
from weakref import WeakKeyDictionary

from control.panopticon import Panopticon
from control.defaults import DEFAULT_PANOPTICON

from ..dsl import StepChain
from blueprint.pipeline.codex_pipeline import PipelineCompiler, PipelineMap
from .factory import build_codex_binding
from .models import CodexConfig, Fn, Phase
from blueprint.linker.codex_binding import CodexBinding


@dataclass(slots=True, init=False)
class Codex:
    """
    Declarative semantic pipeline descriptor.

    Steps
    -----
    Each element of `steps` is:

        • StepChain DSL (SET >> f >> g | ERROR)
        • or bare function (Fn), treated as an implicit Section in
          the default phase (currently Phase.SET).

    strict
    ------
    - True: strict mode (direct calls only)
    - False: interpreted mode (Panopticon required)
    - None: auto (interpreted if semantics used anywhere)

    panopticon
    ----------
    Optional explicit Panopticon. If omitted, Codex injects a control-layer
    default when interpreted mode is required.
    """

    steps: Tuple[StepChain | Fn, ...]
    default: Any = None
    strict: Optional[bool] = None
    panopticon: Panopticon | None = None

    compiler: PipelineCompiler = field(default_factory=PipelineCompiler, init=False)
    _values: WeakKeyDictionary = field(default=None, init=False)
    _pipelines: Dict[type, PipelineMap] = field(default_factory=dict, init=False)

    _owner: Optional[Type] = field(default=None, init=False)
    _name: Optional[str] = field(default=None, init=False)

    _binding: Optional[CodexBinding] = field(default=None, init=False)

    # ------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------
    def __init__(
        self,
        *steps: StepChain | Fn,
        default: Any = None,
        strict: Optional[bool] = None,
        panopticon: Panopticon | None = None,
    ) -> None:
        if not steps:
            raise ValueError("Codex requires at least one step.")

        self.steps = tuple(steps)
        self.default = default
        self.strict = strict
        self.panopticon = panopticon

        self.compiler = PipelineCompiler()
        self._values = WeakKeyDictionary()
        self._pipelines = {}
        self._binding = None
        self._owner = None
        self._name = None

    # ------------------------------------------------------------
    # Class-level sugar: Codex[...] → Codex(...)
    # ------------------------------------------------------------
    @classmethod
    def __class_getitem__(cls, steps):
        """
        Allow declarative syntax:

            email = Codex[
                SET >> f1 >> f2 | ERROR,
                GET >> g1 | WARN,
            ]
        """
        if not isinstance(steps, tuple):
            steps = (steps,)
        return cls(*steps)

    # ------------------------------------------------------------
    # Descriptor protocol
    # ------------------------------------------------------------
    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._name = name

        domain = f"{owner.__name__}.{name}"
        cfg = CodexConfig(strict=self.strict)

        self._binding = build_codex_binding(
            steps=self.steps,
            domain=domain,
            config=cfg,
        )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        internal = self._values.get(instance, self.default)
        pipelines = self._get_or_build_pipeline(type(instance))
        get_stages = pipelines.get(Phase.GET)

        if not get_stages:
            return internal

        cur = internal
        for fn in get_stages:
            cur = fn(cur)
        return cur

    def __set__(self, instance, value):
        pipelines = self._get_or_build_pipeline(type(instance))
        set_stages = pipelines.get(Phase.SET, [])

        cur = value
        for fn in set_stages:
            cur = fn(cur)

        self._values[instance] = cur

    # ------------------------------------------------------------
    # Pipeline cache + default Panopticon injection
    # ------------------------------------------------------------
    def _get_or_build_pipeline(self, owner: Type) -> PipelineMap:
        if self._binding is None:
            raise RuntimeError("CodexBinding not initialized (missing __set_name__?)")

        if owner in self._pipelines:
            return self._pipelines[owner]

        # Determine effective panopticon for interpreted mode. The
        # PipelineCompiler itself decides whether a given phase is
        # strict or interpreted; if strictly strict, the panopticon
        # is never used.
        eff_pan = self.panopticon or DEFAULT_PANOPTICON

        pipeline = self.compiler.build_pipeline(
            binding=self._binding,
            panopticon=eff_pan,
        )

        self._pipelines[owner] = pipeline
        return pipeline
