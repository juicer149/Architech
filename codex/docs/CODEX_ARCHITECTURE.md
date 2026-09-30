# Architech & Codex – System Design Overview

## 1. Purpose and Philosophy

Architech is a **structural DSL + execution framework** for expressing *data transformation, validation, and policy enforcement* in a way that is:

* declarative
* composable
* backend-agnostic
* explicit about side effects

At its core, the system is built around a strict separation between:

* **Structure**: *what* happens to a value
* **Routing & Semantics**: *what to do with the result*

This separation is inspired by:

* Unix philosophy (pipes vs redirects)
* Compiler architecture (AST / IR vs codegen)
* Functional programming (pure transformations vs effects)
* Python descriptors (GET/SET interception)

---

## 2. High-Level Architecture

The system is composed of four conceptual layers:

```
DSL Syntax  →  Structural IR  →  Codex IR  →  Runtime Execution
```

### Layers

1. **DSL (architech.dsl)**

   * Human-facing, fluent syntax
   * Produces immutable, semantics-free structures

2. **Structural IR**

   * `Section`, `Cluster`, `StepToken`
   * Pure representation of pipeline structure

3. **Codex IR (architech.codex)**

   * `Node`, `Pipeline`, `PhasePlan`
   * Backend-specific execution model

4. **Runtime**

   * `Engine`: executes pipelines
   * `Descriptor`: routes results via Python descriptors
   * `Output`: handles side effects and destinations

---

## 3. Core Concepts

### 3.1 Phase

A **Phase** represents *when* a pipeline is executed in the object lifecycle.

Examples:

* `Phase.SET` – attribute assignment
* `Phase.GET` – attribute access
* `Phase.DELETE` – attribute deletion

Phases are implemented as an `IntFlag` to allow future composition.

---

### 3.2 PhaseToken (DSL Entrypoint)

A `PhaseToken` is the DSL entrypoint for building pipelines:

```python
SET = PhaseToken(Phase.SET)
GET = PhaseToken(Phase.GET)
```

Usage:

```python
SET >> step1 >> step2
```

The DSL itself does **not** interpret phases; it only carries them forward.

---

### 3.3 Step and Pipeline Structure

#### Step

A *Step* is an opaque object at the DSL level.

Each backend defines its own contract for what constitutes a valid Step.

For Codex, a Step **must be callable** and have the shape:

    value -> value | None | Exception

This requirement is enforced during compilation, not in the DSL or runtime.

#### Nested Pipelines

`Codex` instances are callable and therefore valid Steps.

This allows pipelines to be nested and composed:

    PIPELINE1 = Codex(...)
    PIPELINE2 = Codex(...)

    SET >> PIPELINE1 | PIPELINE2

Nested Codex instances always execute their own SET phase when invoked as a Step.


#### Step Relations

Steps can be related structurally using operators:

* `>>` – start a new cluster (PRIMARY)
* `<<` – add FALLBACK to the current cluster
* `|`  – add OR alternative

Example:

```python
SET >> f1 << fb1 | fb2 >> f2 | f2b
```

This produces *clusters* of steps with explicit relations.

---

### 3.4 Section (Structural IR)

A `Section` represents a **phase-specific pipeline**:

```python
Section(
    phase=Phase.SET,
    clusters=(
        (f1 PRIMARY, fb1 FALLBACK, fb2 FALLBACK),
        (f2 PRIMARY, f2b OR),
    ),
    semantic=...
)
```

Key properties:

* Immutable
* Semantics-free
* Backend-agnostic

---

## 4. Semantics and Routing (`@`)

### 4.1 The `@` Operator

The `@` operator attaches **semantic annotations** to a pipeline.

Design rule:

> **Everything after `@` describes routing, policy, or side effects — never structure.**

Examples:

```python
SET >> sanitize >> validate @ ERROR
SET >> parse @ WRITE(dest=User.age)
SET >> f1 @ ERROR @ WRITE(dest=Backend.x)
```

Semantics are merged, not replaced.

---

### 4.2 Principle

A `Principle` is a lightweight semantic label:

```python
Principle(label="error", praxis=Praxis(...))
```

Currently:

* Used as metadata
* Preserved through compilation
* Intended for logging, replay, and future policy engines

---

### 4.3 Output (Routing & Effects)

`Output` describes *what to do with a result*:

```python
Output(
    enable=True,
    dest=SELF | RETURN | DROP | custom,
    hook=callable,
    exception=False,
)
```

Output may optionally enforce a type filter on the produced value.

If a type mismatch or exception occurs:
- the default behavior is strict (raise)
- soft fallback must be explicitly enabled via `use_default=True`


Responsibilities:

* Writing values
* Returning values
* Dropping values
* Raising or handling exceptions
* Triggering side effects

Fast-path sentinels (`SELF`, `RETURN`, `DROP`) are optimized for performance.

---

### 4.4 WRITE as a Semantic Preset

`WRITE(...)` is **not a phase**.

It is a convenience wrapper for:

```python
Output(exception=False, ...)
```

Example:

```python
SET >> sanitize >> validate @ WRITE(dest=User.age)
```

This expresses:

> “Run the SET pipeline, then write the result somewhere.”

### 4.5 Exception Semantics (Design Contract)

Codex enforces a strict and explicit exception model.

At the architectural level, Codex distinguishes between:

* **Raised exceptions**
* **Returned exceptions**

This distinction is fundamental to the system design.

#### Raised exceptions

Exceptions that are *raised* by a Step:

```python
raise ValueError("invalid")
````

are considered **hard failures**.

They:

* always bubble
* are never intercepted or converted
* are not affected by routing, fallbacks, or semantics

Codex does not silence, wrap, or reinterpret raised exceptions.

#### Returned exceptions

Exceptions that are *returned* by a Step:

```python
return ValueError("invalid")
```

are treated as **semantic failure values**.

They:

* participate in FALLBACK and OR logic
* may be routed via exception Outputs
* may be written, returned, or redirected explicitly

This design keeps Python’s native exception semantics intact while
allowing controlled, declarative error handling when explicitly requested.

Boolean values are never used for control flow.
`False` is always treated as a legitimate data value, never as a failure signal.

---

## 5. Compilation (DSL → Codex IR)

The compiler converts `Section` objects into `PhasePlan`s:

```python
PhasePlan(
    phase=Phase.SET,
    pipeline=Pipeline(nodes=[...]),
    principle=...,   # optional
    write=Output(...),
    exc=Output(...),
)
```

Rules:

* Sections with the same phase are merged
* Pipelines are appended in order
* Semantics follow *last-wins per category*
* StepChain without an explicit PhaseToken is implicitly treated as Phase.SET 
  during compilation.

---

## 6. Execution Model

### 6.1 Engine

The `Engine` executes pipelines using **strict-first semantics**:

1. Strict pass:

   * Run only PRIMARY steps
   * Abort on first failure

2. Semantic replay:

   * Enable FALLBACK and OR alternatives
   * First success wins
   * Last exception is preserved

This design enables:

* Fast happy-path execution
* Robust error recovery
* Deterministic behavior

---

### 6.2 Descriptor

`Codex` instances are Python descriptors:

* `__get__` → Phase.GET
* `__set__` → Phase.SET
* `__delete__` → Phase.DELETE

The descriptor:

* selects the correct pipeline
* runs the Engine
* applies Output routing

---

## 7. Data Transformation Between Models

Architech supports **snapshot-based workflows**:

```python
RawUser  →  User  →  Backend
```

Using:

* frozen dataclasses
* WRITE destinations
* Output hooks

This enables:

* schema validation
* sanitization
* policy enforcement
* external synchronization

all in a single, declarative layer.

---

## 8. Design Guarantees

* DSL is pure and immutable
* Side effects are explicit
* Pipelines are composable
* Semantics are inspectable
* Runtime is optimizable

---

## 9. Summary

Architech + Codex form a small but powerful system that combines:

* a fluent DSL
* a structural IR
* a compiler
* a runtime engine
* a routing layer

into a cohesive whole.

The guiding principle is simple:

> **Structure before `@`. Policy after `@`.**

This makes pipelines easy to read, reason about, test, and extend.
