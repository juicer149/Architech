# Architech Loader — Deterministic Loading Architecture

> **Module:** `architech.loader`
>
> Deterministic, backend-agnostic loader engine for structured domain systems.

---

## 🧠 Purpose

The **Architech Loader** defines a deterministic foundation for all entity and configuration loading across an ecosystem.  
It guarantees predictable resolution, traceable diagnostics, and uniform lifecycle semantics across multiple formats such as:

- Python modules (`.py`)
- Structured documents (`.json`, `.yaml`)
- Future extensions (remote APIs, DB sources, etc.)

Every backend — no matter the format — follows the same deterministic contract and is orchestrated by a common `EntityConstructor`.

---

## 🔩 Core Design Principles

| Principle | Description |
|------------|--------------|
| **Determinism first** | Every load operation follows a *fixed phase order* and produces explicit `DiagnosticReport` objects. |
| **Backend-first extensibility** | Each format (Python, JSON, YAML, etc.) defines its own backend under `architech.loader.source.*`. |
| **Declarative separation** | The *Locator* describes “what and where”; the *Context* describes “how”. |
| **No silent failures** | All phases produce structured diagnostic output — never implicit exceptions. |
| **Stateless orchestration** | The orchestrator (`EntityConstructor`) is pure and side-effect free. Backends manage their own caching and enrichment. |
| **Orthogonal integration** | The loader layer can power any domain system (e.g., `securitykit`, `datavault`, `policykit`) without coupling. |

---

## ⚙️ Layer Overview

```

architech/
└── loader/
├── base.py           # Abstract deterministic contract for all loaders
├── engine.py         # EntityConstructor, EntityLocator, EntityContext
├── source/
│   ├── **init**.py   # Backend resolver (maps source → backend class)
│   ├── python.py     # Deterministic loader for Python modules
│   ├── json.py       # (future) JSON loader
│   └── yaml.py       # (future) YAML loader
└── ARCHITECTURE.md   # (this file)

````

---

## 🧩 Architectural Flow

### 1️⃣ Entity Definition

A user or system defines **what** to load using an `EntityLocator`:

```python
locator = EntityLocator(
    base="securitykit.hashing.algorithm",
    filename="argon2",
    entry_name="Argon2",
    source="python",
)
````

This describes:

* `base`: the module or domain root
* `filename`: the entity file (or module) name
* `entry_name`: class or object name inside that file
* `source`: which backend type should handle it

---

### 2️⃣ Context Configuration

A complementary `EntityContext` defines **how** the loader behaves:

```python
context = EntityContext(
    registries={
        "securitykit.hashing.algorithm": {"registry": {"argon2": Argon2}},
    },
    strict_mode=False,
)
```

* **Registries** provide static lookups for deterministic performance.
* **Strict mode** controls whether exceptions should raise or report.

---

### 3️⃣ Deterministic Orchestration

The `EntityConstructor` orchestrates loading deterministically:

```python
constructor = EntityConstructor()
report, instance = constructor.load(locator, context)
```

This triggers the backend resolution pipeline:

```
EntityConstructor
   ↓
Backend Resolver (source → class)
   ↓
Backend Loader (e.g. Python)
   ↓
[ Phase 1: _build_static() ]
[ Phase 2: try_resolve()   ]
[ Phase 3: _build_dynamic() ]
   ↓
DiagnosticReport + Entity
```

---

## 🔄 Loader Lifecycle

All backends subclass `BaseLoader` and inherit its deterministic lifecycle.

### Default Phases

| Phase       | Responsibility                              | Method             |
| ----------- | ------------------------------------------- | ------------------ |
| **Static**  | Check registry or cache for known entity    | `_build_static()`  |
| **Resolve** | Optional deterministic import or path check | `try_resolve()`    |
| **Dynamic** | Fallback reflection, parsing, or I/O        | `_build_dynamic()` |

Each phase must return a `(DiagnosticReport, instance_or_None)` tuple.

---

### Example: Python Backend

```python
class Python(BaseLoader):
    def _build_static(self, path, **kw):
        # lookup in registry
        ...

    def try_resolve(self, path, **kw):
        # direct import without reflection
        ...

    def _build_dynamic(self, path, **kw):
        # reflect classes, instantiate first eligible
        ...
```

This backend supports variant suffixes (`.local`, `.secure`, etc.),
deterministic import caching, and base contract validation.

---

## 🧱 Adding a New Backend

To add support for a new format:

1. **Create** a new file under `architech.loader.source/`
   Example: `source/json.py`

2. **Subclass** `BaseLoader`

   ```python
   from architech.loader.base import BaseLoader

   class JSON(BaseLoader):
       def _build_static(...):
           ...
       def try_resolve(...):
           ...
       def _build_dynamic(...):
           ...
   ```

3. **Register it** in `architech.loader.source.__init__.py`:

   ```python
   def resolve_backend(source: str):
       if source.lower() == "json":
           from architech.loader.source.json import JSON
           return JSON
   ```

4. (Optional) **Define extension behavior** (e.g. `.json`, `.yaml`)
   by overriding `normalize_path()`.

That’s it — your backend will automatically be available to the
`EntityConstructor` through `locator.source`.

---

## 🧮 Registry & Enrichment

* **Registries** are optional dictionaries that map identifiers → classes.
* They allow the loader to skip imports and reflection entirely.
* When dynamic loading succeeds, the loader **auto-enriches** the registry
  in a background thread for future deterministic loads.

```python
registry = {"argon2": Argon2}
loader = Python(registry=registry)
```

---

## 🧪 Diagnostic System

Every phase produces a `DiagnosticReport` with structured metadata:

```python
report, entity = loader.load("securitykit.hashing.algorithm.argon2")

print(report.summary())
```

Each report includes:

* `info`, `warnings`, and `errors`
* phase and loader context
* optional traceback in strict mode

This enables complete **observability and auditability** across all loader operations.

---

## 🧭 Design Trade-offs

| Trade-off                        | Rationale                                                                                |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| **No dynamic plugin discovery**  | Determinism and auditability outweigh convenience. Backends must be explicitly declared. |
| **Synchronous main flow**        | Predictable phase sequencing is easier to reason about than async pipelines.             |
| **Threaded registry enrichment** | Allows dynamic caching without blocking load times.                                      |
| **Explicit contracts**           | Avoids ambiguity in validation (type vs schema).                                         |
| **No reflection magic**          | Every backend defines its import/reflection logic explicitly.                            |

---

## 🧩 Summary

| Component           | Responsibility                           |
| ------------------- | ---------------------------------------- |
| `BaseLoader`        | Defines deterministic abstract lifecycle |
| `Python` (backend)  | Concrete loader for `.py` modules        |
| `EntityLocator`     | Declarative *what and where* descriptor  |
| `EntityContext`     | Declarative *how* configuration          |
| `EntityConstructor` | Stateless orchestrator connecting both   |
| `DiagnosticReport`  | Observable structured result             |
| `resolve_backend()` | Pure resolver: source → backend class    |

---

## 🧠 Key Insight

> **The Architech Loader is not an importer — it’s a deterministic execution contract.**

It exists to ensure that *every* system component —
whether a Python class, JSON schema, or YAML config —
can be loaded, validated, and observed with **zero ambiguity**.

---

## 🧾 Example End-to-End Flow

```python
from architech.loader.engine import EntityConstructor, EntityLocator, EntityContext

locator = EntityLocator(
    base="securitykit.hashing.algorithm",
    filename="argon2",
    entry_name="Argon2",
    source="python",
)

context = EntityContext()

constructor = EntityConstructor()
report, entity = constructor.load(locator, context)

print(report.summary())
```

**Result:**

```
✔ Loaded 'Argon2' from securitykit.hashing.algorithm.argon2
✔ Contract validation passed
✔ Registry enriched asynchronously
```

---

## 🧩 Future Extensions

* `JSON` and `YAML` backends (with schema validation)
* `ENV` backend for environment-based config
* `RemoteLoader` for API or distributed configuration
* Deterministic dependency graph resolver

---

© Architech Systems — deterministic by design.
