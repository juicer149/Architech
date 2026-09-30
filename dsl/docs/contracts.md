# Architech DSL — Contracts

This document defines the **formal contracts** between:

* the **DSL**
* **backend implementations** (e.g. Codex)
* **users of the DSL**

It specifies what each layer **may assume**, **must enforce**, and **must not rely on**.

Anything not explicitly guaranteed here is **not part of the contract**.

---

## 1. Scope

This contract applies to:

* `PhaseToken`
* `StepChain`
* `Section`
* `Relation`
* `StepToken`

It does **not** define execution semantics, routing, validation logic, or error handling behavior.

---

## 2. DSL Guarantees (What the DSL Provides)

### 2.1 Structural Integrity

The DSL guarantees that:

* A `StepChain` always has:
  * exactly one `PhaseToken`
  * one or more clusters
* Each cluster is a tuple of one or more `StepToken` objects
* The **first token of every cluster** has:
  * `relation == Relation.PRIMARY`

The DSL does **not** guarantee correctness beyond structure.

---

### 2.2 Relation Encoding

Within a cluster:

* The first token is always `PRIMARY`
* Subsequent tokens may be:
  * all `FALLBACK`
  * all `OR`

The DSL **allows** these patterns structurally, but does not enforce semantic meaning.

Backends may reject invalid combinations.

---

### 2.3 Immutability

The DSL guarantees that:

* `StepChain`, `Section`, and `StepToken` are immutable
* All internal collections are tuples
* All operators (`>>`, `<<`, `|`, `@`) return new objects

Backends may cache, reuse, or safely share DSL objects.

---

### 2.4 Semantic Transparency

The DSL guarantees that:

* `semantic` values are:
  * opaque
  * preserved exactly
  * never interpreted or modified
* Multiple semantics may be attached (e.g. via repeated `@`)

The DSL makes **no assumptions** about semantic content.

---

## 3. DSL Non-Guarantees (What the DSL Does NOT Promise)

The DSL does **not** guarantee:

* that steps are callable
* that steps are valid for any backend
* that relations are semantically meaningful
* that pipelines are executable
* that exceptions are handled in any specific way
* that routing exists or behaves in a certain manner

The DSL is **structural only**.

---

## 4. Backend Obligations (What Backends MUST Do)

A backend consuming the DSL (e.g. Codex) MUST:

### 4.1 Validate Step Values

The backend MUST define:

* what constitutes a valid “step”
* how step validity is checked

Example (Codex):

```python
step_predicate = callable
````

The DSL does not enforce this.

---

### 4.2 Enforce Relation Semantics

The backend MUST decide:

* how `PRIMARY`, `FALLBACK`, and `OR` are interpreted
* whether mixed relations are allowed
* how failure/success is defined

If the backend requires invariants (e.g. homogeneous relations),
it MUST enforce them explicitly.

---

### 4.3 Handle Phases Explicitly

Backends MUST:

* interpret `Section.phase` according to their own phase system
* reject unsupported phase keys
* define default phase behavior if applicable

The DSL does not define default phases.

---

### 4.4 Handle Semantics Explicitly

Backends MUST:

* explicitly recognize semantic tokens they care about
* ignore or reject unknown semantic values

The DSL will not normalize or validate semantics.

---

## 5. Codex-Specific Contract (Documented Dependency)

Codex relies on the following **explicit DSL contract**:

### 5.1 StepChain Contract

Codex assumes that `StepChain` exposes:

```python
@property
def has_phase(self) -> bool

def to_section(*, phase=None) -> Section
```

Rules:

* If `has_phase` is False, Codex MAY supply a default phase
* `to_section(phase=...)` MUST raise if a phase is already present

This contract is **owned by the DSL**.

---

### 5.2 Section Contract

Codex assumes that:

* `Section.phase` is a backend-agnostic phase key
* `Section.clusters` obey structural rules
* `Section.semantic` is opaque

Codex MUST NOT assume more than this.

---

## 6. Error Responsibility

| Error Type               | Responsibility  |
| ------------------------ | --------------- |
| Invalid DSL syntax       | DSL             |
| Invalid structural state | DSL             |
| Invalid step value       | Backend         |
| Invalid semantic token   | Backend         |
| Execution failure        | Backend/runtime |
| Routing behavior         | Backend/runtime |

The DSL raises errors **only** for structural misuse.

---

## 7. Stability Promise

This contract is **intentionally minimal**.

Future changes must obey:

* no semantic leakage into DSL
* no backend assumptions added implicitly
* explicit versioning if contracts change

If behavior is not written here, it is **not guaranteed**.

---

## 8. Summary

The Architech DSL is:

* structural
* immutable
* backend-agnostic
* semantics-free

Backends are:

* responsible for meaning
* responsible for validation
* responsible for execution

> The DSL describes **shape**, not **behavior**.
