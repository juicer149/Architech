# Architech & Codex

Architech is a **declarative DSL and execution framework** for expressing data transformation, validation, and policy enforcement pipelines in Python.

It is designed to make *what happens to data* explicit, composable, and inspectable — while keeping *side effects and routing* strictly controlled.

At its core, Architech combines:

* a fluent **DSL** for building pipelines
* a small **compiler** that produces an execution model (IR)
* a **runtime engine** with strict, deterministic semantics
* deep integration with **Python descriptors** (GET / SET / DELETE)

---

## Key Ideas

* **Structure before semantics**
* **Pure pipelines, explicit effects**
* **Fast happy path, robust fallback path**
* **Descriptor-driven lifecycle integration**

A pipeline describes *how a value flows*.  
Routing describes *what to do with the result*.

These concerns are deliberately separated.

---

## Quick Example

```python
from architech.dsl import PhaseToken
from architech.codex import Codex, Phase
from architech.codex.presets import ERROR

SET = PhaseToken(Phase.SET)
GET = PhaseToken(Phase.GET)

NAME = Codex(
    (SET >> strip >> validate_name) @ ERROR,
    (GET >> normalize_name),
)

class User:
    name = NAME
````

What this means:

* On attribute assignment (`user.name = ...`):

  * run `strip` → `validate_name`
  * errors are routed via `ERROR`

* On attribute access (`user.name`):

  * run `normalize_name`

No hidden side effects. No implicit behavior.

---

## Architecture Overview

```
DSL Syntax  →  Structural IR  →  Codex IR  →  Runtime Execution
```

### Layers

1. **DSL (`architech.dsl`)**

   * Human-facing syntax
   * Produces immutable, backend-agnostic structures

2. **Structural IR**

   * `Section`, `Cluster`, `StepToken`
   * Pure representation of pipeline structure

3. **Codex IR (`architech.codex.ir`)**

   * `Node`, `Pipeline`, `PhasePlan`
   * Execution-oriented model

4. **Runtime (`architech.codex.runtime`)**

   * `Engine`: executes pipelines
   * `DescriptorRouting`: applies routing and side effects

---

## Phases

A **Phase** represents *when* a pipeline runs:

* `Phase.SET` – attribute assignment
* `Phase.GET` – attribute access
* `Phase.DELETE` – attribute deletion

Pipelines are compiled and stored **per phase**.

If no phase is explicitly specified in the DSL, **`Phase.SET` is assumed by default**.

---

## Pipelines and Steps

### Step

A step is typically a callable:

```python
value -> value | None | Exception
```

The DSL does not enforce meaning. Interpretation happens in Codex.

### Relations

Steps can be related structurally:

* `>>` – start a new cluster (PRIMARY)
* `<<` – add FALLBACK
* `|`  – add OR alternative

Example:

```python
SET >> f1 << fb1 | fb2 >> f2 | f2b
```

This describes *structure only*, not behavior.

---

## Semantics and Routing (`@`)

Everything **after `@`** describes *policy and routing*, never structure.

Examples:

```python
SET >> parse >> validate @ ERROR
SET >> transform @ WRITE(dest=User.value)
```

Semantics are merged using **last-wins per category**.

---

## Output and Error Semantics

`Output` controls what happens to results **and exceptions**:

* write to instance (`SELF`)
* return value (`RETURN`)
* drop value (`DROP`)
* custom destinations via hooks

### Exception Model (Important)

Codex makes a strict distinction between **returned exceptions** and **raised exceptions**:

* **Returning an exception**

  ```python
  return ValueError("invalid")
  ```

  * is a *semantic failure*
  * participates in FALLBACK / OR routing
  * may be handled or redirected via `Output(is_exception=True, ...)`

* **Raising an exception**

  ```python
  raise ValueError("invalid")
  ```

  * is a *hard failure*
  * always bubbles
  * is never swallowed or converted implicitly

Codex **never silences raised exceptions**.

If you want Codex to handle failures, your step must **return** the exception object.

> Boolean values are never used for control flow.
> `False` is treated as legitimate data, not a failure signal.

If you want to *capture or store* exceptions instead of raising them, route them explicitly:

```python
SET >> step @ Output(is_exception=True, dest=LOG)
```

---

## Execution Model

The runtime engine uses **strict-first semantics**:

1. **Strict pass**

   * run PRIMARY steps only
   * abort immediately on failure

2. **Semantic replay** (if needed)

   * enable FALLBACK and OR paths
   * first success wins
   * last exception preserved

This yields:

* fast success cases
* deterministic recovery
* predictable behavior

---

## Nested Pipelines

`Codex` objects are callable and can be nested:

```python
PIPELINE = Codex(strip >> validate)

USER_NAME = Codex(
    PIPELINE | fallback_pipeline @ ERROR
)
```

When used as a step, a `Codex` executes its **SET phase only**.

**Guideline:**
Nested Codex pipelines should generally represent a single phase.

---

## Snapshot-Based Architecture (Recommended Pattern)

Codex is designed to work naturally with **immutable, snapshot-based models**, especially frozen dataclasses.

Instead of mutating objects through time, Architech encourages:

```
Input → Policy Snapshot → Validated Model → Backend Representation
```

### Policy Snapshot

```python
from dataclasses import dataclass
from architech.codex import Codex

@dataclass(frozen=True)
class Argon2Policy:
    time_cost = Codex(TIME_COST_RULES @ TO_BACKEND)
    memory_cost = Codex(MEMORY_COST_RULES @ TO_BACKEND)
```

This object:

* is immutable
* contains validation and transformation rules
* has no side effects
* represents a **policy checkpoint**

### Backend Snapshot

```python
@dataclass(frozen=True)
class Argon2Backend:
    time_cost: int
    memory_cost: int
```

Each stage produces a **new, validated snapshot**.

This pattern provides:

* clear boundaries
* easy testing
* safe sharing
* explicit data flow

Policy and backend models may be merged for smaller systems, but separation is encouraged for clarity and auditability.

---

## Guarantees

Architech guarantees:

* immutable DSL structures
* explicit side effects
* phase-aware execution
* inspectable semantics
* backend separation

---

## Documentation

* `ARCHITECTURE.md` – system design and philosophy
* `docs/semantics.md` – execution and error semantics
* `README.md` – overview and usage

---

## Status

Architech & Codex are **intentionally small**.

The goal is not feature breadth, but:

> correctness, clarity, and long-term evolvability.

---

## License

Architech & Codex are licensed under the **MIT License**.
