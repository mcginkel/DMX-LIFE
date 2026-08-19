# Architecture Decision Records

This directory records the architectural decisions behind DMX Life — what was
decided, why, and what it cost us.

Most of these were written retroactively in August 2026, reconstructing
decisions that were made during the original build. They describe the system
**as built**, not as idealised. Where a decision has known problems, the
Consequences section says so plainly rather than quietly omitting it.

## Format

Each record follows a lightweight [Nygard-style](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
template: Context → Decision → Consequences → Alternatives considered.

**Status** values:

- `Accepted` — in force today.
- `Accepted (known risk)` — in force, but with a documented downside we have
  chosen to live with for now.
- `Superseded by ADR-XXXX` — no longer in force.

## Index

### Core

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-json-file-as-system-of-record.md) | JSON file as the system of record | Accepted |
| [0002](0002-artnet-via-direct-socket-sends.md) | Art-Net output via direct socket sends | Accepted |
| [0003](0003-continuous-dmx-output-thread.md) | Continuous DMX output from a dedicated thread | Accepted |
| [0004](0004-fixed-linear-crossfade.md) | Fixed-duration linear crossfade | Accepted |
| [0005](0005-layered-scene-state.md) | Server-authoritative layered scene state | Accepted |
| [0006](0006-scene-groups.md) | Scene groups with exclusive and additive semantics | Accepted |
| [0007](0007-sparse-overlay-via-empty-enabled-fixtures.md) | Sparse overlays via empty `enabledFixtures` | Accepted (known risk) |
| [0008](0008-scenes-as-full-channel-arrays.md) | Scenes stored as full 512-value arrays | Accepted (known risk) |

### Supporting

| ADR | Title | Status |
|-----|-------|--------|
| [0009](0009-fixture-types-in-code.md) | Fixture types defined in Python code | Accepted |
| [0010](0010-fixture-linking-by-index.md) | Fixture linking by array index | Accepted (known risk) |
| [0011](0011-server-rendered-vanilla-frontend.md) | Server-rendered Jinja with vanilla JavaScript | Accepted |
| [0012](0012-app-factory-with-module-singletons.md) | App factory with module-level singletons | Accepted |
| [0013](0013-http-basic-auth.md) | HTTP Basic Auth with hardcoded credentials | Accepted (known risk) |

## Related documentation

- [`openspec/specs/`](../../openspec/specs/) — behavioural specifications
  (what the system does, in testable terms).
- [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) — a module map and orientation
  guide. It points into these ADRs for rationale rather than duplicating it,
  so the two shouldn't disagree; if they ever do, the ADRs are correct.
