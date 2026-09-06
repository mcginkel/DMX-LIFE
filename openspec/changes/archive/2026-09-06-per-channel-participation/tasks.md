## 0. Before starting

- [x] 0.1 Back up `app/config.json`. Standing practice, and this change edits
      and saves scenes as part of verifying it.

## 1. Track claim state per channel

- [x] 1.1 In `app/static/js/scenes.js`, hold a per-channel claimed flag rather
      than deriving participation from the fixture checkbox alone.
- [x] 1.2 On opening a scene, a channel is claimed if and only if its number
      is a key in the scene's stored map. Do not widen to whole fixtures.
- [x] 1.3 On creating a new scene, every channel of every fixture starts
      claimed, matching today's "all fixtures enabled" default.
- [x] 1.4 Populate slider values from the map for claimed channels, and from
      the fixture type's default for unclaimed ones.

## 2. Claim and release from the row

- [x] 2.1 Clicking a channel row toggles whether that channel is claimed.
- [x] 2.2 The toggle must not fire when the operator is using the slider -
      neither a click on it nor a drag across it may change claim state.
- [x] 2.3 A claimed row renders at full strength with a solid bar; an
      unclaimed row is dimmed with an unlit bar. The difference must not be
      carried by hue alone.
- [x] 2.4 An unclaimed channel shows no value rather than `0`, so a
      deliberate zero and an unclaimed channel are visibly different.
- [x] 2.5 Toggling a claim updates the live preview, so the operator hears
      about it from the rig as well as the screen.

## 3. The fixture control becomes a summary

- [x] 3.1 Show, per fixture, whether all, none or some of its channels are
      claimed - using the checkbox's indeterminate state for "some".
- [x] 3.2 Toggling the fixture control claims or releases all of that
      fixture's channels in one action.
- [x] 3.3 The summary updates as individual rows are claimed and released.

## 4. Save exactly what is claimed

- [x] 4.1 The save payload contains exactly the claimed channels, each with
      its current value, including zeros.
- [x] 4.2 No widening: a partially claimed fixture contributes only its
      claimed channels.
- [x] 4.3 The preview (`Test Scene`) sends the same set the save would, so
      what is heard is what is stored.

## 5. Verify

- [x] 5.1 **The bug**: open `extraLampSpreker`, save it without changing
      anything, and confirm it still claims exactly channels 34, 36, 40, 47
      and 49 - not 26 channels.
- [x] 5.2 **No regression**: open a whole-fixture scene (`Blauw`), save it
      unchanged, and confirm its stored map is byte-identical to before.
- [x] 5.3 Perf3 and Perf4 show as partially claimed when `extraLampSpreker`
      is open, not as fully selected.
- [x] 5.4 Claim one extra channel in a partial scene, save, reopen, and
      confirm exactly that channel was added.
- [x] 5.5 Release a channel from a whole-fixture scene, save, reopen, and
      confirm exactly that channel was removed and the fixture now reads as
      partially claimed.
- [x] 5.6 A claimed channel at zero survives a round trip and is not confused
      with an unclaimed one - check an `Uit` scene specifically, since those
      depend on deliberate zeros.
- [x] 5.7 Dragging a slider never toggles a claim.
- [x] 5.8 Toggling the fixture control still claims or releases the whole
      fixture in one action.
- [x] 5.9 All 18 scenes still activate correctly on the main page after the
      editor changes - the composition path is untouched, but confirm it.
