# ADR-0005: Server-authoritative layered scene state

- **Status:** Accepted
- **Date:** 2026-08-18

## Context

The original model tracked a single `active_scene` string. Activating a scene
called `build_dmx_buffer(name, current_values)`, which started from whatever
was currently on the wire and wrote the new scene's channels on top.

This worked for one-scene-at-a-time operation but broke down as soon as scenes
were meant to combine. The venue's real operating pattern is layered: a main
look on the Performers and Pars, a background colour on the Tribars, an
atmosphere wash, and an occasional extra lamp for the speaker — chosen
independently and combined live.

Two concrete failures:

1. **No memory of what was underneath.** Because each activation layered onto
   the live buffer, nothing recorded *why* a channel held its value. Turning
   something off was impossible: there was no state to fall back to.
2. **Zero values could not be expressed.** The sparse path
   (see [ADR-0007](0007-sparse-overlay-via-empty-enabled-fixtures.md)) skipped
   falsy values (`if value:`), so an "off" overlay wrote nothing at all.

The trigger was the extra speaker lamp, which touches five channels inside two
fixtures that a main scene also controls. Applying it the normal way would zero
the main scene's colour on those fixtures; there was no way to remove it again.

## Decision

Make the server authoritative over a **set of active scene layers**, and
recompute the entire DMX frame from that set on every change.

`SceneManager` holds `active_layers`, an insertion-ordered dict of scene names
(oldest first). `toggle_scene(name)`:

1. If the scene is already active, remove it.
2. Otherwise, if it belongs to an exclusive group, remove that group's current
   member, then add this one (see [ADR-0006](0006-scene-groups.md)).
3. Rebuild a fresh `bytearray(512)` from zero by replaying every remaining
   active layer in insertion order.
4. Hand the finished buffer to `DMXController.set_with_transition()`.

The API returns the full list of active scene names, and the frontend mirrors
that list rather than tracking highlight state itself. Page reloads render
highlights from the same server-side list.

## Consequences

**Good:**

- **Turning a layer off is well defined.** Its channels fall back to whatever
  the remaining layers specify, or to 0 if nothing claims them — because the
  frame is rebuilt from scratch, not patched.
- The rule is uniform. There is no special-case code for the extra lamp; it is
  just a layer in a group of one.
- Server and browser cannot disagree about what is active, since the browser
  never computes the state.
- The behaviour is now easy to reason about and to test: given a set of layers,
  the output frame is a pure function of that set.

**Bad:**

- **Layer order matters and is implicit.** Later layers overwrite earlier ones
  on contested channels, and the order is activation order, not a declared
  priority. Toggling A then B can differ from B then A. This is not surfaced in
  the UI.
- Rebuilding all 512 channels on every toggle is more work than patching a few,
  though at human click rates this is irrelevant.
- `active_layers` lives only in memory. Restarting the server loses the current
  look, and the lights hold their last frame until something is activated.
- `test_scene()` from the editor still writes directly to the DMX buffer
  without touching `active_layers`, so the tracked state and the wire disagree
  until the next toggle.

## Alternatives considered

- **Priority numbers per scene.** Removes the order ambiguity, at the cost of
  another field to configure and reason about. Worth doing if ordering ever
  actually bites.
- **Client-side layer tracking.** Rejected: two browsers, or a reload, would
  immediately disagree about the truth.
- **HTOP/LTP merge semantics like a real console.** Highest-takes-precedence
  merging is the industry norm for multi-source DMX. Overkill here, and
  last-takes-precedence matches what an operator expects when clicking buttons.
