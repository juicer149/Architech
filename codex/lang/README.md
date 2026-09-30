# Codex Language Layer (`codex.lang`)

This package defines the **language primitives** of Codex.

It is intentionally minimal.

## What lives here

- Phase tokens (`SET`, `GET`, `DELETE`)
- Routing primitives for outputs (write / return / drop)
- Semantic vocabulary (`Principle`, `Praxis`, ERROR / WARNING / INFO)

These constructs define **how Codex is expressed**, not **what it should do**.

## What does NOT live here

- Validators
- Transformers
- Composite pipelines
- Domain rules (email, numbers, strings, etc.)

Those belong in `stdlib/codex/` or user code.

## Design goals

- Backend-agnostic
- Opinion-light
- Stable contracts
- Suitable for embedding in other systems

Think of this layer as:

> “The grammar and vocabulary of Codex.”
