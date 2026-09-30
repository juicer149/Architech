# Architech DSL

Architech DSL is a **pure, backend-agnostic structural language** for describing pipelines.

It defines **shape, ordering, and relationships** between steps — but **no execution semantics**.

The DSL is designed to be:

* immutable
* declarative
* semantics-free
* reusable across multiple backends

Codex is one such backend, but the DSL does **not** depend on Codex.

---

## What the DSL Is

The DSL provides:

* a **PhaseToken** abstraction (e.g. `SET`, `GET`)
* structural node types:
  * `Relation`
  * `StepToken`
  * `Section`
* a fluent syntax for building pipelines:
  ```python
  SET >> f1 << fb1 | fb2 >> f2 | f2b @ semantic
````

The output of the DSL is an immutable **`Section`** object that backends can compile into their own IR.

---

## What the DSL Is Not

The DSL does **not**:

* execute steps
* validate step types (e.g. callable vs non-callable)
* handle exceptions
* define routing or control flow
* interpret semantics
* depend on Codex or any runtime

All behavior lives in **backend implementations**.

---

## Core Concepts

### PhaseToken

A `PhaseToken` represents a logical phase boundary.

Backends define their own phase keys:

```python
from enum import Enum, auto
from dsl import PhaseToken

class Phase(Enum):
    SET = auto()
    GET = auto()

SET = PhaseToken(Phase.SET)
GET = PhaseToken(Phase.GET)
```

The DSL does not interpret the phase key — it merely preserves it.

---

### Step

A **step** is an opaque value.

The DSL does not assume steps are callable.

Examples of valid step values (from the DSL’s perspective):

* functions
* objects
* configuration tokens
* symbolic identifiers

Backends decide what a valid step is.

---

### StepChain

`StepChain` is an immutable builder used to construct `Section` objects.

Operators:

| Operator | Meaning                                    |                                   |
| -------- | ------------------------------------------ | --------------------------------- |
| `>>`     | start a new cluster with a PRIMARY step    |                                   |
| `<<`     | add a FALLBACK step to the current cluster |                                   |
| `        | `                                          | add an OR or FALLBACK alternative |
| `@`      | attach semantic metadata                   |                                   |

Example:

```python
pipeline = (
    SET
    >> sanitize
    << recover
    | alternative
    >> validate
) @ "error-policy"
```

Every operator returns a **new StepChain**.

---

### Relation

Relations describe **structural intent**, not behavior:

* `PRIMARY` — main step
* `FALLBACK` — alternative used on failure
* `OR` — alternative choice

The DSL does not define what “failure” or “success” means.

---

### Section

A `Section` is the immutable structural result of a StepChain:

```python
Section(
    phase=SET.key,
    clusters=(
        (StepToken(...), StepToken(...)),
        (StepToken(...),),
    ),
    semantic=...
)
```

A backend compiles `Section` objects into executable plans.

---

## Semantics (`@`)

Semantics are **opaque annotations** attached to a Section.

The DSL:

* stores them
* preserves ordering
* never interprets them

Backends may use semantics for:

* error handling
* routing rules
* logging
* tracing
* policies

Example:

```python
SET >> f1 >> f2 @ {"timeout": 30} @ {"retries": 3}
```

---

## Immutability Guarantees

The DSL guarantees:

* all core objects are immutable
* all internal collections are tuples
* no operator mutates state

This allows:

* safe reuse
* caching
* deterministic compilation

---

## Layered Architecture

```
DSL syntax        →  StepChain
Structural IR     →  Section
Backend IR        →  (e.g. Codex Node / Pipeline)
Runtime           →  execution + effects
```

Each layer has a **single responsibility**.

---

## Contracts

Formal contracts are defined in:

```
dsl/docs/contracts.md
```

This document specifies:

* what the DSL guarantees
* what backends must enforce
* what is explicitly *not* promised

If behavior is not documented there, it is not part of the contract.

---

## Why a Separate DSL Package?

The DSL lives outside Codex intentionally:

* avoids semantic coupling
* allows multiple backends
* keeps execution concerns isolated
* enables reuse in other domains

Codex depends on the DSL — not the other way around.

---

## Summary

Architech DSL is a **structural language**, not a framework.

It answers:

> *“What is the shape of this pipeline?”*

Backends answer:

> *“What does this pipeline mean?”*
