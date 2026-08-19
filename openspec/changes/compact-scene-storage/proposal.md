## Why

`app/config.json` stores each scene's channels as a flat 512-entry array,
almost entirely zeros. Measured against the real config: 186 KB total, 144 KB
of it scenes, of which 97% of the stored values are zero
([ADR-0008](../../../docs/adr/0008-scenes-as-full-channel-arrays.md)).

The array format also forces `enabledFixtures` to carry two unrelated
meanings depending on whether it's empty
([ADR-0007](../../../docs/adr/0007-sparse-overlay-via-empty-enabled-fixtures.md)):
non-empty means "copy this fixture's full range, zeros included"; empty
means "sparse overlay, only non-zero values, ignore fixture boundaries."
That split exists only because an array can't distinguish "channel
deliberately set to zero" from "channel this scene has no opinion about" -
every position holds *some* value whether the scene means it or not.

Storing each scene as an explicit `{channel: value}` map fixes both at once:
a channel's *presence* as a key means "this scene claims it," independent of
whether its value happens to be zero, which removes the need for two
different composition rules.

## What Changes

- Scene `channels` becomes a map of channel number → value (1-512 → 0-255),
  not a 512-entry array. Only channels a scene actually claims are stored.
- `enabledFixtures` is no longer stored. "Which fixtures does this scene
  affect" becomes fully derivable from which channels appear in the map -
  an enabled fixture's *entire* range is always written (zeros included),
  same as today's non-empty-`enabledFixtures` behavior, so the fact of
  inclusion round-trips without a separate field.
- `SceneManager`'s two composition rules (fixture-scoped copy vs.
  sparse-overlay) collapse into one: write every entry present in the map;
  leave everything else untouched. **BREAKING** at the data-model level for
  anything reading `config.json` directly (nothing outside this codebase
  does).
- The scene editor UI keeps the same per-fixture checkbox interaction
  operators already use. What changes is underneath: checking a fixture
  means its channels get written to the map (zero or not) on save; leaving
  it unchecked means its channels never become map keys. Reopening a scene
  for editing re-derives which checkboxes were on from which channels are
  present.
- The save/test API request and response shape for scene channels changes
  from an array to the same map shape, end-to-end - not just the on-disk
  format. See design.md for why a backend-only translation layer was
  rejected.
- Existing scenes migrate automatically on load (same pattern as
  `fix-fixture-link-references`'s link migration): accept the old array
  shape, convert in memory, log what happened, persist the new shape on the
  next save.

## Non-goals

- **Sub-fixture partial-channel selection in the editor UI.** One scene
  today (`extraLampSpreker`) claims specific channels inside a fixture
  without claiming the whole thing - not expressible through a per-fixture
  checkbox. This isn't a regression: that scene was never creatable through
  the editor UI even today, only by hand-authoring JSON directly, and
  remains exactly as possible (no more, no less) under the new format. A
  per-channel editing affordance is a natural future extension, not part of
  this change.
- **Changing scene toggling, grouping, or layer-composition-order
  semantics.** Those are independent of how a single scene's channels are
  stored; `scene-control`'s toggle/group/ordering requirements are
  unaffected.
- **Changing how configuration is written to disk** (still the atomic
  temp-file + rename from `atomic-config-writes`). Only the JSON shape
  changes, not the write mechanism.

## Capabilities

### Modified Capabilities
- `scene-control`: the "Fixture-scoped channel application" and "Sparse
  overlay application" requirements described two composition modes that
  existed only because of the array format; both are removed and replaced
  by one requirement describing map-based application.
- `scene-authoring`: "Per-fixture participation" and "Channel value
  validation" describe the array-and-`enabledFixtures` shape explicitly and
  need to describe the map shape instead.

## Impact

- Affected code: `app/scene_manager.py` (`_apply_scene` collapses to one
  rule), `app/config_manager.py` (migration on read), `app/views/setup.py`
  (`find_invalid_channel` validates a map), `app/dmx_controller.py`
  (`test_scene` consumes a map), `app/static/js/scenes.js` (sliders read
  from and write to a map; checkbox state is derived, not stored
  separately), `app/config.json` (migrated in place on next save).
- Validated against the real, current config before proposing this: 242
  realistic layer combinations (every scene solo, every
  main×achtergrond×sfeer×extra combination the running app actually
  supports) produce byte-identical output between today's dual-rule
  composition and the proposed single-rule version. Projected size:
  scenes 144 KB → 19 KB (86.5%), whole `config.json` 186 KB → 61 KB (67%).
