# ADR-0010: Fixture linking by array index

- **Status:** Accepted (known risk)
- **Date:** 2026-08-18 (documented retroactively)

## Context

The rig contains groups of identical fixtures that are almost always driven
together: six Performer 2000s, eight Compac Pars, four Tribars. Setting the
same value on eight sliders, eight times, for every scene, is tedious and
error-prone.

## Decision

Each fixture may carry a `linked_to` field holding the **0-based array index**
of another fixture in the `fixtures` list, or `null`. The referenced fixture is
the "master".

Linking is enforced and applied entirely in the browser:

- `fixtures.js` restricts the link dropdown to fixtures of the same type,
  refuses to link a fixture to itself, and refuses to link to a fixture that
  already has children — preventing chains and cycles.
- `scenes.js` mirrors slider movements from a master onto its children in real
  time while editing.
- On fixture deletion, `fixtures.js` nulls out links pointing at the deleted
  fixture and decrements every index above it.

The backend stores and returns the field but never interprets it. Scene
application does not consult `linked_to` at all — by the time a scene is saved,
the linked values are already baked into its `channels` array.

## Consequences

**Good:**

- Building a scene for eight identical pars is one slider movement.
- Because the values are materialised at save time, the DMX output path stays
  simple and linking cannot introduce runtime surprises.
- The same-type and no-chaining rules keep the mental model flat: one master,
  N children, one level deep.

**Bad:**

- **Positional references are fragile.** The index is the fixture's position in
  a JSON array, so any reordering invalidates every link. The deletion path
  compensates by rewriting indices, but it runs only in the browser — editing
  `config.json` by hand, or any future server-side reordering, silently
  corrupts the links.
- **The current data is already wrong.** In `config.json`, `Perf3` has
  `linked_to: 2` while itself sitting at index 2, and `Par2` has `linked_to: 7`
  at index 7 — both self-links, which the UI is supposed to reject. The
  Performer and Par groups look uniformly off by one, consistent with an
  index shift that was not fully applied. Because linking only affects the
  editor, this has never affected a show, which is exactly why it went
  unnoticed.
- **All the integrity rules live in JavaScript.** The API accepts any
  `linked_to` value, including self-links, cycles, cross-type links and
  out-of-range indices.
- The relationship is one-directional and implicit; there is no group object, so
  "which fixtures move together" must be derived by scanning for children.

## Alternatives considered

- **Reference by fixture name.** Names are already the stable identifier used
  by `enabledFixtures`, and would survive reordering. This is the obvious fix,
  and would also let the existing broken links be repaired by inspection.
  Requires a migration and rename handling.
- **Explicit fixture groups** as first-class config objects. Better matches the
  intent ("these eight pars are one unit"), supports multi-level grouping, and
  could drive the scene editor directly. A larger change to both storage and UI.
- **Server-side validation of links.** Cheap and worth doing regardless of which
  representation is used — it would have caught the self-links above.
