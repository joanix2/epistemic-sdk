---
name: epistemic-harness
description: Use when running or extending the Epistemic SDK development harness — scripts/harness.py, validation levels, task contracts, or invariant checks.
---

# Epistemic SDK Harness

Workflow for running and extending the multi-agent development harness of Epistemic SDK.

## Commands

```bash
python -m unittest discover -s tests -v      # contract tests
python -m examples.nat_language               # M2/M1 example
python scripts/harness.py check               # imports, public-interface integrity, invariants
python scripts/harness.py run                 # run tests (dev-cache aware)
python scripts/harness.py run --no-cache      # force execution, bypass cache
```

## Validation levels

Progress from narrow to broad; never claim an unimplemented level is operational:

1. Unit tests of data structures and interfaces.
2. Contract tests between components.
3. Algebraic properties of M3 (only once implemented).
4. M2 language definitions.
5. M1 program execution.
6. Validation, falsification, revision.
7. End-to-end epistemic loop.

## Task contract (delegation)

Emit a contract with: Task ID, objective, allowed file scope, interfaces involved, invariants to preserve, acceptance criteria, tests to run, dependencies to read, indicative budget.

## Report (return)

Modifications, affected interfaces, tests run and results, verified properties, uncertainties, regression risks, decisions needed.

See `docs/harness/PROTOCOL.md` for the full protocol and `docs/harness/CACHE.md` for cache/invalidation policy.
