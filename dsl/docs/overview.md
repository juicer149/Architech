# Architech DSL — Overview

The Architech DSL is a **purely structural language** for describing pipelines.

It is intentionally **semantics-free**, **backend-agnostic**, and **immutable**.

The DSL does **not** execute code.
The DSL does **not** interpret failures.
The DSL does **not** know what a “step” means.

Its sole responsibility is to describe **structure**.

---

## What the DSL Is

The DSL provides a compact, fluent syntax for expressing **how steps are related**:

```python
SET >> f1 << fb1 | fb2 >> f2 | f2b @ semantic
````

From this, the DSL produces immutable structural objects:

* `StepToken`
* `Cluster`
* `Section`

These objects can be consumed by **any backend** that understands how to interpret them.

The DSL itself does not impose meaning on:

* phases
* steps
* relations
* semantics
* exceptions
* return values

All interpretation happens **outside** the DSL.

---

## What the DSL Is Not

The DSL is **not**:

* a validation system
* an execution engine
* a policy engine
* a routing system
* a type system
* a control-flow language

Specifically:

* The DSL does **not** require steps to be callables
* The DSL does **not** define what failure means
* The DSL does **not** catch or raise exceptions
* The DSL does **not** decide fallback behavior
* The DSL does **not** know what `None`, `False`, or `Exception` signify

Those concerns belong to the backend (e.g. Codex).

---

## Core Design Principle

> **Structure first. Semantics later.**

The DSL captures *shape*, not *behavior*.

This separation allows:

* multiple execution models
* strict layering
* testable compilation
* inspectable pipelines
* long-term evolution without semantic drift

---

## Phases

A **PhaseToken** is the entrypoint into the DSL:

```python
SET = PhaseToken(Phase.SET)
GET = PhaseToken(Phase.GET)
```

A phase token:

* wraps a backend-defined phase key
* carries that key through the DSL unchanged
* has no intrinsic meaning in the DSL

The DSL does not interpret phases — it only preserves them.

---

## Steps

In the DSL, a **step** is an opaque value:

```python
Step = Any
```

Common backend interpretations include:

* callables
* rule objects
* configuration descriptors
* symbolic identifiers

The DSL never inspects or validates steps.

---

## Relations

Steps are related structurally using three relations:

* **PRIMARY**
* **FALLBACK**
* **OR**

These relations describe **position and grouping only**.

They do not imply:

* execution order
* failure semantics
* retry logic
* exception handling

Those meanings are defined by the backend.

---

## Clusters

A **cluster** is a tuple of `StepToken` objects that are structurally related.

Example:

```text
[f1 PRIMARY, fb1 FALLBACK, fb2 FALLBACK]
```

or:

```text
[f2 PRIMARY, f2b OR]
```

The DSL guarantees only that:

* clusters preserve order
* each token has an explicit relation

No further invariants are enforced at the DSL level.

---

## Sections

A **Section** represents a phase-specific pipeline:

```python
Section(
    phase=phase_key,
    clusters=(cluster1, cluster2, ...),
    semantic=optional_metadata,
)
```

Key properties:

* immutable
* backend-agnostic
* semantics-free
* safe to inspect and transform

A `Section` is the **final product** of the DSL.

---

## Semantics (`@`)

The `@` operator attaches **opaque semantic metadata** to a Section:

```python
(SET >> f1 >> f2) @ semantic_token
```

Rules:

* semantics are never interpreted by the DSL
* semantics are stored verbatim
* multiple semantics may be merged structurally

The meaning of semantics is entirely backend-defined.

---

## Backend Contract (High-Level)

Backends consuming the DSL may rely on the following guarantees:

* `StepChain` materializes into a `Section`
* `Section.phase` is always set
* clusters are ordered tuples
* relations are explicit and stable
* no execution has occurred

Backends must **not** assume:

* step callability
* exception semantics
* control-flow meaning
* routing behavior

These belong outside the DSL.

---

## Summary

The Architech DSL is a **structural frontend**, nothing more and nothing less.

It exists to make pipeline structure:

* explicit
* inspectable
* immutable
* backend-independent

All meaning is deferred.

> If you want behavior, look at the backend.
> If you want structure, you are in the right place.
