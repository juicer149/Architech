# Codex Execution Semantics

## Codex as Descriptor

When a Codex instance is assigned to a class attribute, it acts as a
Python descriptor:

* **set** → Phase.SET
* **get** → Phase.GET
* **delete** → Phase.DELETE

Routing rules (SELF, RETURN, DROP, custom destinations) apply only
in this mode.

---

## Codex as Step (Callable)

A Codex instance may also be used as a Step inside another Codex pipeline.

Example:

```python
PIPELINE = Codex(
    sanitize >> validate
)

USER_NAME = Codex(
    PIPELINE | fallback_pipeline @ ERROR
)
```

### Rules

* When invoked via `__call__`, Codex executes **only Phase.SET**
* GET / DELETE pipelines are ignored
* No descriptor routing is active
* Codex behaves as a pure transformation: `value → value`

### Guideline

Nested Codex pipelines should define only Phase.SET behavior.

If phase-specific behavior is required, it must be expressed at the
outer Codex level:

```python
Codex(
    SET >> pipeline_set,
    GET >> pipeline_get,
)
```

---

## Failure Model: Return vs Raise

Codex makes a **strict distinction** between *semantic failure* and
*programmer/system failure*.

### Returned Exceptions (Semantic Failure)

A Step may **return** an exception instance to indicate a recoverable,
semantic failure:

```python
def is_int(v):
    if not isinstance(v, int):
        return ValueError("not an int")
    return v
```

Returned exceptions:

* are captured by the Engine
* participate in FALLBACK / OR logic
* are routed via the configured **exception Output** (`exc`)
* may be written, returned, dropped, or replaced by defaults

This is the *intended* way to integrate with Codex error handling.

---

### Raised Exceptions (Hard Failure)

If a Step **raises** an exception, it is treated as a *hard failure*:

```python
def is_int(v):
    if not isinstance(v, int):
        raise TypeError("not an int")
    return v
```

Raised exceptions:

* immediately bubble out of Codex
* bypass semantic routing
* are **never** swallowed or rewritten

This preserves Python’s normal error model and prevents silent bugs.

---

## Capturing Exceptions as Values (Advanced)

If you *want* to work with exceptions **as data**, Codex allows this
explicitly via `Output`.

By configuring the *exception output channel*, you can route exceptions
to a destination instead of raising them:

```python
SET >> parse @ Output(
    is_exception=True,
    dest=RETURN,
)
```

or write them somewhere:

```python
SET >> parse @ Output(
    is_exception=True,
    dest=MyErrorStore,
    hook=lambda exc, inst, field: MyErrorStore.log(exc),
)
```

In this mode:

* exceptions are treated as values
* routing rules apply
* the error does **not** bubble

This is **opt-in behavior** and must be explicit.

---

## Design Rationale

* No implicit error swallowing
* No boolean-based control flow (`False` is a valid domain value)
* Clear separation between validation failure and programming error
* Compatible with Python exceptions
* Predictable, debuggable pipelines

**Rule of thumb:**

> *Return exceptions to participate in Codex semantics.*
> *Raise exceptions to abort execution.*
