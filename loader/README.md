# Architech Loader

> Deterministic, backend-agnostic entity loader for structured domains.

---

## 🧠 Overview

The **Architech Loader** provides a unified, deterministic way to load and
instantiate entities — whether they are Python classes, JSON documents,
YAML configurations, or remote structures.

It serves as the **foundation layer** for all domain systems in Architech,
ensuring that every load operation is:

- Predictable  
- Observable  
- Extensible  
- Validated  

Unlike traditional import systems, the Architech Loader is a **contract** —
not a convenience wrapper. Every backend follows the same deterministic
lifecycle and reports structured diagnostic information at every step.

---

## ⚙️ Quick Example

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
report, instance = constructor.load(locator, context)

print(report.summary())
````

**Output:**

```
✔ Loaded Argon2 from securitykit.hashing.algorithm.argon2
✔ Contract validation passed
✔ Registry enriched asynchronously
```

---

## 🧩 Architecture Summary

| Component           | Responsibility                                           |
| ------------------- | -------------------------------------------------------- |
| `EntityLocator`     | Declarative “what and where” descriptor                  |
| `EntityContext`     | Declarative “how” configuration                          |
| `EntityConstructor` | Stateless orchestrator that drives the lifecycle         |
| `BaseLoader`        | Abstract deterministic contract (shared by all backends) |
| `source/`           | Backend implementations (e.g. Python, JSON, YAML)        |
| `resolve_backend()` | Stateless resolver that maps `source → backend`          |

Every backend implements a three-phase deterministic lifecycle:

1. **Static** — registry-based lookup
2. **Resolve** — deterministic import or existence check
3. **Dynamic** — reflection, parsing, or I/O discovery

Each phase produces a `DiagnosticReport` and optional instance.

---

## 🧱 Extending the Loader

To add support for a new source format (e.g. `json`, `yaml`, `env`):

1. Create a new backend under `architech.loader.source/`
2. Subclass `BaseLoader` and implement:

   ```python
   def _build_static(...): ...
   def try_resolve(...): ...
   def _build_dynamic(...): ...
   ```
3. Add it to the resolver in `source/__init__.py`

That’s all — your backend is now automatically discoverable
by the `EntityConstructor` through its `source` field.

---

## 📚 Documentation

For a detailed architectural walkthrough, design philosophy, and backend
extension guide, see:

👉 [**ARCHITECTURE.md**](./ARCHITECTURE.md)

---

## 🧩 Philosophy

> “Determinism over convenience.
> Explicit contracts over implicit behavior.
> Observability over magic.”

The Architech Loader is the foundation of a predictable runtime system —
built to make loading, introspection, and validation fully transparent.

---

© Architech Systems — deterministic by design.
