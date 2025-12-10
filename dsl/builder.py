# ================================================================
# architech/dsl/builder.py
# ================================================================
"""
StepChain — fluent DSL builder for Sections.

This class builds up an abstract pipeline like:

    SET >> f1 << fb1 | fb2 >> f2 | f2b @ semantic_token

The DSL itself is semantics-free:

- No exceptions, no validation rules
- No Principle/Praxis logic
- No execution concerns

Backends (Codex, or others) map the resulting Section into their own
IR and execution semantics.

Operator semantics
------------------

Given a PhaseToken `SET` and step objects `f1`, `fb1`, `alt`:

    • ">>" (right shift)
        Starts a new *cluster* with a PRIMARY token.

            SET >> f1 >> f2
        → two clusters:
            ( [f1 PRIMARY], [f2 PRIMARY] )

    • "<<" (left shift)
        Adds a FALLBACK token to the current (last) cluster.

            SET >> f1 << fb1
        → one cluster:
            [f1 PRIMARY, fb1 FALLBACK]

    • "|" (bitwise or)
        Adds an OR- or FALLBACK-style token to the current cluster:

            - If the previous token in the cluster has relation
              PRIMARY or OR:
                → new token gets relation OR.

            - If the previous token has relation FALLBACK:
                → new token gets relation FALLBACK
                  (i.e. an additional fallback alternative).

        Examples:

            SET >> f1 | f2 | f3
        → cluster:
            [f1 PRIMARY, f2 OR, f3 OR]

            SET >> f1 << fb1 | fb2 | fb3
        → cluster:
            [f1 PRIMARY, fb1 FALLBACK, fb2 FALLBACK, fb3 FALLBACK]

    • "@" (matrix multiply)
        Attaches an opaque `semantic` token to the whole Section.

            (SET >> f1 >> f2) @ semantic

        The semantic object is stored on the resulting Section and
        interpreted by the backend.

        NOTE: due to Python's operator precedence, it is recommended
        to parenthesize the chain when using "@", as in the example
        above.

Immutability
------------

StepChain is implemented as an *immutable builder*:

    - Every operator (>>, <<, |, @) returns a NEW StepChain instance.
    - Internal state is stored in tuples, not lists.

This makes StepChain instances safe to share, cache and reason about
functionally.

You can think of:

    PhaseToken + StepChain + Section

as the structural / “middle layer” between human-friendly DSL syntax
and backend-specific IR (such as Codex's SectionSpec/ClusterSpec).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple

from .nodes import StepToken, Relation, Cluster, Clusters, Section
from .phases import PhaseToken
from .protocol import Step


@dataclass(frozen=True, slots=True)
class StepChain:
    """
    Immutable builder for a phase-specific Section.

    Internally the structure is:

        Section(
            phase=phase_token.key,
            clusters=(
                (StepToken(...), StepToken(...)),  # cluster 0
                (StepToken(...),),                 # cluster 1
                ...
            ),
            semantic=<optional semantic>,
        )
    """

    phase_token: PhaseToken
    _clusters: Clusters
    _semantic: Any | None = None

    def __init__(self, phase_token: PhaseToken, first: Step):
        """
        Create a new StepChain with a single PRIMARY token in the first cluster.
        """
        object.__setattr__(self, "phase_token", phase_token)

        first_token = StepToken(value=first, relation=Relation.PRIMARY)
        first_cluster: Cluster = (first_token,)

        object.__setattr__(self, "_clusters", (first_cluster,))
        object.__setattr__(self, "_semantic", None)

    # ------------------------------------------------------------------
    # Internal constructor for persistence
    # ------------------------------------------------------------------
    @classmethod
    def _from_state(
        cls,
        phase_token: PhaseToken,
        clusters: Clusters,
        semantic: Any | None,
    ) -> "StepChain":
        """
        Internal helper to build a new StepChain from existing state.

        Used by the operator implementations to preserve immutability.
        """
        inst = cls.__new__(cls)
        object.__setattr__(inst, "phase_token", phase_token)
        object.__setattr__(inst, "_clusters", clusters)
        object.__setattr__(inst, "_semantic", semantic)
        return inst

    # ------------------------------------------------------------------
    # Core syntax operators
    # ------------------------------------------------------------------

    def __rshift__(self, step: Step) -> "StepChain":
        """
        Start a new cluster with `step` as PRIMARY.

        Example:

            SET >> f1 >> f2
        """
        new_token = StepToken(value=step, relation=Relation.PRIMARY)
        new_cluster: Cluster = (new_token,)
        new_clusters: Clusters = self._clusters + (new_cluster,)
        return StepChain._from_state(self.phase_token, new_clusters, self._semantic)

    def __lshift__(self, step: Step) -> "StepChain":
        """
        Add a FALLBACK token to the current (last) cluster.

        Example:

            SET >> f1 << fb1
        """
        if not self._clusters:
            raise ValueError("Cannot add fallback without an existing cluster.")

        *prefix, last_cluster = self._clusters

        new_token = StepToken(value=step, relation=Relation.FALLBACK)
        updated_last: Cluster = last_cluster + (new_token,)
        new_clusters: Clusters = tuple(prefix) + (updated_last,)
        return StepChain._from_state(self.phase_token, new_clusters, self._semantic)

    def __or__(self, step: Step) -> "StepChain":
        """
        Add an OR- or FALLBACK-style token to the current (last) cluster.

        Relation rules:

            - If there is no existing token in the cluster:
                → new token gets relation PRIMARY (degenerate case).

            - If the last token in the cluster is PRIMARY or OR:
                → new token gets relation OR.

            - If the last token is FALLBACK:
                → new token gets relation FALLBACK
                  (an additional fallback alternative).
        """
        if not self._clusters:
            raise ValueError("Cannot add OR-step without an existing cluster.")

        *prefix, last_cluster = self._clusters

        if not last_cluster:
            relation = Relation.PRIMARY
        else:
            last_token = last_cluster[-1]
            if last_token.relation is Relation.FALLBACK:
                relation = Relation.FALLBACK
            else:
                relation = Relation.OR

        new_token = StepToken(value=step, relation=relation)
        updated_last: Cluster = last_cluster + (new_token,)
        new_clusters: Clusters = tuple(prefix) + (updated_last,)
        return StepChain._from_state(self.phase_token, new_clusters, self._semantic)

    def __matmul__(self, semantic: Any) -> "StepChain":
        """
        Attach an opaque semantic token to this chain.

        The semantic value will be stored on the resulting Section.
        """
        return StepChain._from_state(self.phase_token, self._clusters, semantic)

    # ------------------------------------------------------------------
    # Materialization
    # ------------------------------------------------------------------

    def to_section(self) -> Section:
        """
        Materialize this StepChain to an immutable Section.

        The resulting structure has the phase key at the top:

            Section(
                phase=self.phase_token.key,
                clusters=self._clusters,
                semantic=self._semantic,
            )

        Backends can treat this as a phase-specific pipeline and
        convert it to their own IR.

        In a layered architecture, you can think of:

            DSL syntax (StepChain) → Section (structural IR) → Codex IR → Engine
        """
        return Section(
            phase=self.phase_token.key,
            clusters=self._clusters,
            semantic=self._semantic,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def clusters(self) -> Clusters:
        """
        Return the current tuple of clusters.

        Primarily useful for debugging and tests.
        """
        return self._clusters

    def __repr__(self) -> str:
        return (
            f"StepChain(phase={self.phase_token.key!r}, "
            f"clusters={self._clusters!r}, semantic={self._semantic!r})"
        )
