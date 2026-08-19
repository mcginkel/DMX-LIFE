# Repair and harden fixture link references

## Why

The `linked_to` field stores a 0-based index into the `fixtures` array
([ADR-0010](../../../docs/adr/0010-fixture-linking-by-index.md)). The values
currently in `app/config.json` are wrong:

| Fixture | Array index | `linked_to` | Points at |
|---|---|---|---|
| `Perf3` | 2 | 2 | **itself** |
| `Perf4` | 3 | 2 | `Perf3` |
| `Perf5` | 4 | 2 | `Perf3` |
| `Perf6` | 5 | 2 | `Perf3` |
| `Par2` | 7 | 7 | **itself** |
| `Par3`–`Par8` | 8–13 | 7 | `Par2` |

The intent is plainly that the Performers follow `Perf2` (index 1) and the Pars
follow `Par1` (index 6). Every value in both groups is one too high, which is
the signature of an index shift that was applied to the data but not to the
links — exactly the failure mode ADR-0010 warns about.

Two of the resulting links are self-references, which the editor's own rules are
supposed to make impossible. They exist because the rules live only in
JavaScript: the API accepts any integer, including a fixture's own index, an
out-of-range value, or one that forms a cycle.

This has never affected a show, because `linked_to` only drives slider
synchronisation in the scene editor and is never consulted when composing DMX
output. The consequence is narrower but still real: editing a Performer or Par
scene does not propagate values the way the operator expects, so the "adjust one
fixture, the rest follow" workflow silently does the wrong thing — and the
values it produces get baked into saved scenes.

## What changes

- Change `linked_to` from an array index to the master fixture's **name**, which
  is already the stable identifier used by `enabledFixtures`.
- Migrate `config.json` on load: convert existing integer values to names,
  repairing the off-by-one by inferring the intended master where the stored
  index is self-referential.
- Validate links server-side on save: the master must exist, be a different
  fixture, be of the same type, and not itself be linked.
- Keep the browser rules as they are; they become a convenience rather than the
  only defence.

## Non-goals

- Introducing first-class fixture groups. ADR-0010 identifies that as the better
  long-term model, but it changes the editor substantially; this change fixes the
  correctness problem within the existing design.
- Changing how linked values are applied while editing. The propagation
  behaviour is correct; only the references it follows are wrong.
- Making DMX output consult links. Values remain materialised into scenes at
  save time.

## Impact

- Affected specs: `fixture-configuration`
- Affected code: `app/config_manager.py` (migration), `app/views/setup.py`
  (validation), `app/static/js/fixtures.js` and `app/static/js/scenes.js`
  (name-based lookups), `app/models/fixture.py`, `app/config.json`.
- **Migration is one-way.** Take a backup of `config.json` before running it.
- The repair depends on inferring intent from the current data. The inference is
  stated explicitly in the design so it can be checked rather than trusted.
