# Design: fixture link references

## Context

Two problems are entangled here: the stored data is wrong, and the
representation makes that kind of wrongness easy. Fixing only the data leaves
the next reorder free to break it again; fixing only the representation leaves
the current links broken.

Both are fixed together, because the migration has to touch every value anyway.

## Decisions

### Reference by name, not index

`enabledFixtures` already identifies fixtures by name, and scenes survive
reordering because of it. Using names for `linked_to` makes the two consistent
and removes the entire class of index-shift bugs — including the deletion
renumbering logic in `fixtures.js`, which exists only to compensate for the
positional representation.

Names are not formally unique today. In practice they are, because the editor
lists them and an operator would not create two fixtures called `Par1`. The
validation added here should enforce uniqueness on save, which is worth having
regardless.

### The repair inference, stated plainly

The migration cannot simply read the stored indices, because they are wrong. It
infers the intended master as follows:

1. If `linked_to` is an integer pointing at a **different** fixture of the
   **same type**, take that fixture's name. (Correct links migrate unchanged.)
2. If `linked_to` points at the fixture **itself**, treat it as off-by-one and
   take the fixture at `linked_to - 1`, provided that fixture is of the same
   type. This maps `Perf3 → Perf2` and `Par2 → Par1`.
3. If the result is still invalid, set `null` and log a warning naming the
   fixture, rather than guessing further.

Rule 2 is the one carrying an assumption. It is safe here because the shift is
uniform across both affected groups and the resulting masters — `Perf2` and
`Par1` — are the first member of each group, which is what an operator would
pick. **This should be verified by eye against the migrated file, not trusted.**

Expected outcome for the current data:

| Fixture | Before | After |
|---|---|---|
| `Perf3`–`Perf6` | `2` | `"Perf2"` |
| `Par2`–`Par8` | `7` | `"Par1"` |
| `Tribar3` | `15` | `"Tribar2"` |
| `Tribar4` | `16` | `"Tribar3"` |
| `Sfeer rechts` | `18` | `"Sfeer Links"` |

Note that `Tribar3` and `Tribar4` currently resolve to `Tribar2` and `Tribar3`
under rule 1 — the latter making `Tribar4` a child of a fixture that is itself
linked, which the no-chaining rule forbids. Whether the intent was for both to
follow `Tribar1` is a question for the operator, not an inference the migration
should make. Rule 3 applies: leave it, warn, and let it be set in the UI.

### Migrate on load, once

The migration runs in `ConfigManager` when a fixture's `linked_to` is an
integer, and the result is written back on the next save. Accepting both shapes
on read means a config from before the change still loads.

## Risks

- **The inference repairs the wrong link.** Mitigated by writing the before/after
  table to the log and requiring visual verification against the table above.
- **Duplicate fixture names would make a name ambiguous.** Mitigated by
  enforcing uniqueness on save; existing duplicates are reported rather than
  silently resolved.
- **Frontend and backend disagreeing during the transition.** Both must land
  together; the JS lookups are `fixtures[index]` today and become name lookups.

## Alternatives considered

- **Repair the indices, keep the representation.** Smaller change, but leaves
  the fragility in place and keeps the renumbering logic that caused this.
- **Stable per-fixture IDs.** More robust than names, since renaming would not
  break links. Rejected as heavier than the problem warrants — and names already
  serve this role for scenes.
- **Leave it alone.** Genuinely defensible: the impact is confined to editor
  convenience. Rejected because the broken behaviour is silent, and silent
  wrongness in a tool an operator trusts is worse than a visible fault.
