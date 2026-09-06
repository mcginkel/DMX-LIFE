## Context

The stored format already expresses everything this change needs. A scene is a
`{channel: value}` map, and `extraLampSpreker` claims five channels scattered
inside two fixtures. What cannot express it is the editor, whose only notion of
participation is a per-fixture checkbox.

That gap is currently destructive, not merely limiting. The editor derives its
checkboxes from "does any of this fixture's channels appear in the map", so it
shows Perf3 and Perf4 as participating, and saving writes all twenty-six of
their channels - turning a five-channel accent into a block that forces
twenty-one channels to zero. No warning, no visible difference at save time.

The shape of the real usage matters for the design: seventeen of eighteen
scenes claim whole fixtures, and one does not. Whatever is added must leave the
common case exactly as cheap as it is today.

## Goals / Non-Goals

**Goals:**
- A partially claimed scene survives being opened and saved. This is the bug.
- Sub-fixture claims can be authored, not merely preserved.
- Selecting or releasing a whole fixture stays a single action.
- The stored format does not change.

**Non-Goals:**
- Any change to composition at output time. `_apply_scene` already writes
  exactly the claimed channels; it has never been the problem.
- Any change to the stored format. This makes the editor able to say what the
  storage could always represent.
- Copying a claim pattern between fixtures, or claim presets. If sub-fixture
  authoring turns out to be common, that is the follow-up; today one scene
  uses it.

## Decisions

### Claim state lives on the row, and the row is the control

Clicking a channel row toggles whether the scene claims that channel. There is
no per-channel checkbox.

Chosen over a checkbox column because the editor already scrolls a long way -
twenty fixtures, up to thirteen channels each - and 128 new controls is a
serious cost to serve a case that arises in one scene. Chosen over
"moving a slider claims it" because a scene must be able to claim a channel
deliberately *at zero*: that is precisely what the `Uit` scenes rely on, and a
slider-implies-claim rule cannot express it without an extra affordance anyway.

The discoverability cost is real and accepted: clicking a row is not
self-evident. It is mitigated by the state being obvious once seen, and by the
whole-fixture control remaining the primary path.

### Claimed and unclaimed differ by more than colour

An unclaimed row is dimmed and carries an unlit bar; a claimed row is at full
strength with a solid bar. That is a lightness difference plus a non-colour
marker, following the same rule the theme refresh established after three
palettes proved indistinguishable to this operator.

An unclaimed channel shows no value rather than `0`. A claimed channel at zero
and an unclaimed channel are different things - the first forces the lamp dark,
the second leaves it to other layers - and showing `0` for both would hide the
distinction the whole change exists to make.

### The fixture control becomes a three-state summary

Per fixture: all channels claimed, none, or some. Toggling it claims or
releases the whole fixture in one action, which is how every existing scene is
authored and how it will stay.

"Some" is a state the control reports but the operator cannot select directly -
it arises from claiming individual rows. A control that can display a state it
cannot be set to is slightly unusual, and the alternative - a three-way cycle
through all/none/partial - would be worse, since "partial" has no meaningful
default set of channels.

### Save writes exactly what is claimed

No inference, no widening. The payload is the claimed set with each claimed
channel's current value, including zeros. This is what removes the destructive
behaviour: a scene that claimed five channels claims five after a round trip
because the editor never had an opinion about the other twenty-one.

## Risks / Trade-offs

- **A whole fixture can be released by accident**, since rows are now
  clickable and the editor previews live. A misclick changes what the scene
  will store. → The change is visible immediately (the row dims, the preview
  drops that channel) and is undone by clicking again. Not saved until Save is
  pressed.
- **Clicking a row is not discoverable.** → Accepted, per the decision above.
  Worth revisiting if it is not obvious in use.
- **The interaction competes with the slider.** A channel row contains a range
  input, and clicking near it must adjust the value rather than toggle the
  claim. → The toggle must be bound to the parts of the row that are not the
  slider, and dragging the slider must never be interpreted as a claim toggle.
- **Existing whole-fixture scenes must not change.** Seventeen scenes are
  fully claimed and must round-trip byte-identically. → This is the primary
  regression check, not an afterthought.

## Open Questions

- Whether the fixture-level control should stay a checkbox showing an
  indeterminate state, or become something that reads more clearly as a
  three-state summary. Worth seeing in use before deciding.
