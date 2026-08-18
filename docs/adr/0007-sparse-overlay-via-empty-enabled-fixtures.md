# ADR-0007: Sparse overlays via empty `enabledFixtures`

- **Status:** Accepted (known risk)
- **Date:** 2026-08-18 (documented retroactively; semantics load-bearing since 2026-08-18)

## Context

A scene stores a 512-entry `channels` array plus an `enabledFixtures` list of
fixture names. When applying a scene, `SceneManager` needs to know which
channels the scene actually claims — a scene that only controls the Tribars
must not zero the Performers.

The normal answer is `enabledFixtures`: for each named fixture, copy that
fixture's whole channel range from the scene into the frame, including zeros.
That is what makes a background colour scene able to say "green is 0 here".

The extra speaker lamp broke this. It touches five channels — 34, 36, 40, 47
and 49 — which fall *inside* the ranges of two Performer fixtures that main
scenes also drive. Naming those fixtures in `enabledFixtures` would copy their
entire 13-channel blocks, zeroing the main scene's colour. Naming no fixtures
had to mean something different.

## Decision

Overload the empty `enabledFixtures` list to mean **sparse overlay**:

- **Non-empty `enabledFixtures`** — fixture-scoped application. For each named
  fixture, copy every channel in its range verbatim, zeros included. Channels
  outside those fixtures are untouched.
- **Empty `enabledFixtures`** — sparse application. Copy only the channels
  whose value is non-zero (`if value:`), regardless of fixture boundaries.

Currently exactly one scene uses the sparse form: `extraLampSpreker`.

## Consequences

**Good:**

- The extra lamp can sit on top of any main scene without disturbing the rest
  of the fixtures it shares channels with.
- No schema change and no migration; existing scenes kept working unchanged.
- Combined with [ADR-0005](0005-layered-scene-state.md), removing a sparse
  overlay is well defined — the frame is rebuilt without it.

**Bad:**

- **One field carries two unrelated meanings**, and the distinction is
  invisible in `config.json`. A scene saved from the editor with every fixture
  checkbox unchecked silently becomes a sparse overlay rather than an empty
  scene. This is the sharpest edge in the data model.
- **A sparse scene cannot express an explicit zero.** Because the sparse path
  tests truthiness, value 0 is indistinguishable from "not claimed". This is
  precisely why `extraLampSpreker` has no companion "off" scene — turning it
  off is done by removing the layer, not by applying zeros.
- The old pre-layering code used the same `if value:` test on the *live* buffer,
  which is what made "off" impossible before ADR-0005. The trap is now
  contained, not removed.
- Nothing in the UI explains or exposes the distinction.

## Alternatives considered

- **An explicit `mode: "sparse" | "fixtures"` field.** Says what it means,
  allows explicit zeros in sparse scenes, and removes the accidental-overlay
  trap. This is the right fix and should be done when the scene schema is next
  touched; it needs a migration for existing scenes.
- **A `channelMask` list of claimed channel numbers.** Fully general — sparse
  scenes could then set 0 deliberately. More expressive, but a bigger schema
  change and more editor work.
- **Give the extra lamp its own fixtures in the patch.** Would avoid the
  overlapping-range problem entirely, but misrepresents the physical rig: those
  channels really do belong to the Performer fixtures.
