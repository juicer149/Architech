# Architech DSL — Grammar

This document defines the **exact grammar and operator semantics** of the Architech DSL.

It describes **how expressions are parsed into structure**, not how they are executed.

All semantics described here are **purely structural**.

---

## Lexical Elements

The DSL operates on four kinds of elements:

* **PhaseToken**
* **Step**
* **Semantic token**
* **Operators**: `>>`, `<<`, `|`, `@`

The DSL does not impose meaning on these elements — it only relates them structurally.

---

## Entry Point

Every DSL pipeline **must begin with a PhaseToken**.

Example:

```python
SET >> f1
````

This produces a `StepChain` bound to `SET.key`.

The DSL does not allow “phase-less” chains.

---

## Steps

A **step** is an opaque value:

```python
Step = Any
```

The DSL does not inspect, validate, or interpret steps.

Backends may impose additional constraints (e.g. callability).

---

## Operators

### `>>` — Start New Cluster (PRIMARY)

**Syntax:**

```python
chain >> step
```

**Meaning:**

* Starts a **new cluster**
* Inserts `step` as a `PRIMARY` token in that cluster

**Example:**

```python
SET >> f1 >> f2
```

**Structure:**

```text
clusters = (
    [f1 PRIMARY],
    [f2 PRIMARY],
)
```

---

### `<<` — Add FALLBACK to Current Cluster

**Syntax:**

```python
chain << step
```

**Meaning:**

* Adds `step` to the **current (last) cluster**
* Assigns relation `FALLBACK`

**Example:**

```python
SET >> f1 << fb1
```

**Structure:**

```text
clusters = (
    [f1 PRIMARY, fb1 FALLBACK],
)
```

**Notes:**

* A cluster must already exist
* `<<` never creates a new cluster

---

### `|` — Add OR or FALLBACK Alternative

**Syntax:**

```python
chain | step
```

**Meaning:**

Adds an alternative to the current cluster.

The relation assigned depends on the **previous token** in the cluster:

| Previous relation | New relation |
| ----------------- | ------------ |
| PRIMARY           | OR           |
| OR                | OR           |
| FALLBACK          | FALLBACK     |

**Examples:**

```python
SET >> f1 | f2 | f3
```

**Structure:**

```text
[f1 PRIMARY, f2 OR, f3 OR]
```

```python
SET >> f1 << fb1 | fb2 | fb3
```

**Structure:**

```text
[f1 PRIMARY, fb1 FALLBACK, fb2 FALLBACK, fb3 FALLBACK]
```

**Notes:**

* `|` never starts a new cluster
* The DSL allows OR and FALLBACK to be structurally distinct
* Interpretation of OR vs FALLBACK is backend-defined

---

### `@` — Attach Semantic Metadata

**Syntax:**

```python
chain @ semantic
```

**Meaning:**

* Attaches opaque semantic metadata to the **entire Section**
* Does not modify structure

**Example:**

```python
(SET >> f1 >> f2) @ semantic_token
```

**Rules:**

* Semantics are stored verbatim
* The DSL does not interpret semantics
* Multiple semantics may be attached via repeated `@`

---

## Operator Precedence

Python operator precedence applies.

Important consequence:

```python
SET >> f1 >> f2 @ semantic
```

is parsed as:

```python
SET >> f1 >> (f2 @ semantic)   # ❌ invalid
```

Therefore, **parentheses are required**:

```python
(SET >> f1 >> f2) @ semantic   # ✅ correct
```

This is not a DSL rule — it is a Python grammar rule.

---

## Immutability Rules

The DSL is **purely functional**:

* Every operator returns a **new StepChain**
* No operator mutates existing state
* Internal structures use tuples, not lists

This guarantees:

* referential transparency
* safe reuse
* predictable compilation

---

## Materialization

A `StepChain` materializes into a `Section`:

```python
section = chain.to_section()
```

This produces:

```python
Section(
    phase=<phase key>,
    clusters=<tuple of clusters>,
    semantic=<semantic or None>,
)
```

This is the **final DSL product**.

---

## Error Conditions (DSL-Level)

The DSL raises errors only for **structural violations**:

* adding `<<` or `|` without an existing cluster
* malformed internal state (should not occur in normal usage)

The DSL never raises errors related to:

* step execution
* type checking
* exception handling
* routing behavior

---

## Summary

The Architech DSL grammar is:

* minimal
* explicit
* structural
* semantics-free

It describes **how steps are related**, not **what they do**.

All meaning is deferred to the backend.

> If something is not explicitly stated here, the DSL does not define it.
