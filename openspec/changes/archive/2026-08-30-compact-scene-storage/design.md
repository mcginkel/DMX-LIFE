## Context

See proposal.md - Why for the size numbers and the `enabledFixtures` dual-
meaning problem this also resolves. Two things shape the approach:

1. Physical DMX output is inherently positional - a backend's `send()` still
   needs a concrete 512-byte frame ([`add-pluggable-dmx-backends`](../add-pluggable-dmx-backends/),
   if that lands first, or the existing `DMXController` either way). Sparse
   storage is a *scene* concept; the frame the wire actually carries stays
   exactly as wide as it is today. Nothing here touches output.
2. This project has hit the "two representations of the same fact can drift"
   problem twice already: `enabledFixtures` vs. the array it was meant to
   gate ([ADR-0007](../../../docs/adr/0007-sparse-overlay-via-empty-enabled-fixtures.md)),
   and positional fixture links vs. what they actually pointed at
   ([ADR-0010](../../../docs/adr/0010-fixture-linking-by-index.md)). The
   design below is shaped by not creating a third instance of that pattern.

## Goals / Non-Goals

**Goals:**
- One representation of "which channels does this scene claim," not two
  (a field plus an array both claiming to say so).
- No behavior change for any of the 18 scenes in the real config - validated
  in explore mode against 242 realistic layer combinations, not just
  asserted.
- The editor's per-fixture checkbox interaction is unchanged from the
  operator's point of view.

**Non-goals:** see proposal.md - Non-goals.

## Decisions

### Full stack, not backend-only translation

Considered keeping the array as the API/editor-facing shape and translating
to/from a sparse map only at the persistence boundary (`ConfigManager`).
Rejected: that's exactly the "two representations, kept in sync by
convention" shape that caused the problem this change exists to fix, just
relocated from `enabledFixtures`-vs-array to disk-format-vs-wire-format.
The map is the shape everywhere - config file, save/test API payloads, and
what the editor reads to build its slider state.

### `enabledFixtures` is derived, not stored

A fixture counts as "enabled" for editor purposes if *any* of its channels
appear as keys in the scene's map. This works cleanly because of how
inclusion is written in the first place (next decision) - an included
fixture always has *all* its channels present, so checking for any one of
them is equivalent to checking for all of them. No separate field, so
nothing to fall out of sync with the map it was describing.

**Alternative considered:** keep `enabledFixtures` stored alongside the map,
purely as a cheap shortcut for re-populating checkboxes without recomputing
from the fixture list. Rejected - it reintroduces a second source of truth
for something fully derivable, which is the specific failure mode this
change is meant to close off, for a computation (checking whether a
fixture's channel numbers intersect the map's keys) that's cheap regardless.

### Inclusion is decided by the checkbox, at save time, per whole fixture

Checking a fixture writes every one of its channels into the map -
including ones a slider left at 0 - because a scene needs to be able to
claim a deliberate zero (this is what makes "Achtergrond Uit" able to
actually darken the Tribars). Unchecking a fixture means none of its
channels become map keys at all. This is the same rule
`SceneManager._apply_scene`'s fixture-scoped branch already applies today;
what changes is that it's now applied once, by the editor, at save time -
not re-derived by two different runtime code paths depending on whether
`enabledFixtures` happened to be empty.

### Composition collapses to one rule

`_apply_scene` no longer branches on `enabledFixtures` or consults the
fixture list at all during composition - it becomes: for each `(channel,
value)` in the active scene's map, `buffer[channel - 1] = value`. Simpler
code, not just smaller data. `_rebuild_buffer` is otherwise unchanged - it
still starts from a fresh `bytearray(512)` and layers active scenes in
activation order, per [ADR-0005](../../../docs/adr/0005-layered-scene-state.md).

### Migration follows the fixture-link precedent

`ConfigManager.read()` gains a scene-channel migration alongside the
existing `_migrate_fixture_links`: for any scene whose `channels` is still a
list (old shape), convert using the same logic already validated in explore
mode - non-empty `enabledFixtures` becomes every claimed fixture's full
range as explicit map entries; empty `enabledFixtures` becomes just the
non-zero entries (that scene was already sparse in spirit, only the
`extraLampSpreker`-shaped case). Log a before/after summary, same as the
fixture-link migration. The converted shape is written back on the next
save, not forced by a one-time script.

### JSON keys are strings - one conversion boundary, not scattered casts

`{channel: value}` serializes with string keys (`"14"`, not `14`) - JSON
object keys are always strings. Every read site converts once, at the point
data enters Python from JSON (`{int(k): v for k, v in raw.items()}`), so the
rest of the codebase works with a genuine `int → int` map and never compares
a string channel number against an int one by accident.

**Alternative considered:** an array of `[channel, value]` pairs instead of
an object. Rejected - an object gives O(1) lookup by channel number for
free and is the more natural JSON shape for a sparse map; the pair-array
shape would need to reinvent that.

## Risks / Trade-offs

- **String/int key confusion** is the sharpest edge in this design - a
  missed conversion produces a channel that silently never matches anything.
  → Mitigated by the single-conversion-boundary decision above; worth an
  explicit unit test asserting no string keys survive past the read
  boundary.
- **Migration correctness** - same class of risk as the fixture-link
  migration, which did have a real subtlety (chain flattening) it needed
  careful validation for. → Same mitigation that worked there: log a
  before/after table, verify by eye against the real config before trusting
  it, keep the `config.json.bak` that `atomic-config-writes` already
  produces as the rollback path.
- **Frontend and backend must land together** - `scenes.js` sending arrays
  to a backend expecting maps (or vice versa) fails outright rather than
  silently, which is preferable to a silent mismatch, but still means this
  isn't a change that can be rolled out in independent halves.

## Migration Plan

1. Land the migration + `SceneManager`/`ConfigManager` changes first,
   keeping the API surface accepting *both* shapes temporarily is not
   worth the complexity given point above (frontend/backend land together)
   - land backend and `scenes.js` in the same change.
2. Verify against the real config: confirm the migration log's before/after
   matches expectations, confirm every scene still activates correctly
   in the browser, confirm `config.json` shrinks as projected.
3. Rollback: revert the commit(s). As with every change touching
   `config.json` this session, take an explicit backup before deploying,
   not just relying on `config.json.bak` from the last write.

## Open Questions

None - the one real ambiguity (how to express partial-fixture selection in
the UI) is resolved as a stated non-goal, not deferred.
