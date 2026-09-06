## Why

Opening the `extraLampSpreker` scene in the editor and saving it silently
destroys it.

That scene claims five channels scattered inside two fixtures - 34 and 36 of
Perf3's range 27-39, and 40, 47 and 49 of Perf4's 40-52. The editor's only
notion of participation is a per-fixture checkbox, and it derives that
checkbox from "does any of this fixture's channels appear in the scene". So it
shows Perf3 and Perf4 as participating, and saving writes *all twenty-six* of
their channels. A five-channel accent becomes a twenty-six-channel block that
forces twenty-one channels to zero, changing what the scene does to the rig.

Nothing warns the operator. The scene is not marked as special, the save
button behaves normally, and the damage is only visible by comparing channel
counts afterwards.

Before `compact-scene-storage`, this scene survived being opened and saved,
because the empty-`enabledFixtures` sparse mode preserved exactly the non-zero
channels. That change named sub-fixture selection as a non-goal on the grounds
that such a scene "was never creatable through the editor UI even today", which
was true - but it was *editable*, and now it is not. This closes that gap.

The underlying limitation is real and predates both changes: the editor can
express "this whole fixture participates" and nothing finer. Any lighting look
that touches part of a fixture - one colour of a tribar, a single cell of a
multi-cell unit - has to be hand-authored in JSON.

## What Changes

- The scene editor gains per-channel participation: within a participating
  fixture, the operator can mark individual channels as claimed or not claimed
  by the scene.
- The per-fixture control becomes a three-state summary of its channels - all
  claimed, none claimed, or some - rather than a binary that rewrites them.
  Toggling it still claims or releases the whole fixture, which keeps the
  common case a single click.
- Saving a scene writes exactly the claimed channels, so a scene that claims
  five channels continues to claim five after a round trip through the editor.
- A scene whose claimed channels do not align to whole fixtures is displayed as
  such rather than being silently rounded up to fixture boundaries.
- **No change to the stored format.** `{channel: value}` already expresses
  partial-fixture claims exactly; this change makes the editor able to say what
  the storage could always represent.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `scene-authoring`: "Per-fixture participation" currently requires that
  selecting a fixture writes *every* channel of that fixture into the scene's
  map, and that the selection is reconstructed from which channels are present.
  Both halves change: participation becomes per-channel, with the per-fixture
  control as a summary over it, and reconstruction has to distinguish a fully
  claimed fixture from a partially claimed one.

## Impact

- Affected code: `app/static/js/scenes.js` (participation state, the
  channel controls, payload construction, checkbox derivation),
  `app/templates/setup/scenes.html` (per-channel control markup).
- Affected data: none. Existing scenes are already stored in a format that
  expresses this; `extraLampSpreker` becomes correctly editable rather than
  needing repair.
- Risk this removes: the current silent widening of a partially-claimed scene
  on save.
- Interaction cost: the editor gains a control per channel where it previously
  had one per fixture. Keeping the common "whole fixture" case a single action
  is a stated requirement, not an afterthought - see design.
- Out of scope: any change to how scenes compose at output time. Composition
  already writes exactly the claimed channels.
