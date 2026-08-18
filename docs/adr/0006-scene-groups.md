# ADR-0006: Scene groups with exclusive and additive semantics

- **Status:** Accepted
- **Date:** 2026-08-18

## Context

Once scenes became layers ([ADR-0005](0005-layered-scene-state.md)), the
question was which combinations are legal. The venue's scenes fall into natural
families:

- **main** — the Performer 2000 and Compac Par looks (`blauw/oranje`,
  `paars/oranje`, `rood/oranje`, plus `Main Uit`).
- **achtergrond** — a single background colour across the four Tribars
  (`red`, `Blauw`, `Green`, `Paars`, `Oranje`, `Turqoise`, `Achtergrond Uit`).
- **sfeer** — the atmosphere wash on the Sfeer fixtures (`sf1`–`sf3`,
  `Sfeer Uit`).
- **aanuit** — `Alles Aan` / `Alles Uit`.
- **extra** — `extraLampSpreker`, an overlay for speaker focus.

Within a family the choices are mutually exclusive: two background colours on
the same fixtures at once is meaningless. Across families they are meant to
combine. The extra lamp is different again — it must be able to sit on top of
any main scene without displacing it.

## Decision

Give every scene an optional `group` field, persisted in `config.json`.

`SceneManager.EXCLUSIVE_GROUPS = {'main', 'achtergrond', 'sfeer', 'aanuit'}`
defines which groups are single-select. Activating a scene in one of these
first deactivates whichever member of that group is currently active.

Any group **not** in that set — currently `extra`, and any scene with no group
at all — is additive: it toggles independently and neither displaces nor is
displaced by anything else.

The main page renders one section per group, in a fixed display order defined
by `GROUP_ORDER` in `app/views/main.py`, with ungrouped scenes collected under
"Other" so nothing can silently disappear from the UI.

## Consequences

**Good:**

- The interface matches how the operator actually thinks: pick a main look,
  pick a background, pick an atmosphere, then optionally add the speaker lamp.
- Exclusivity is enforced server-side, so it holds regardless of what the
  browser does.
- Adding a group is a data change plus one entry in `GROUP_ORDER`; adding an
  *additive* group needs no code change at all.
- Each family gets its own explicit "off" scene (`Main Uit`,
  `Achtergrond Uit`, `Sfeer Uit`), so a family can be cleared without clearing
  the rest.

**Bad:**

- **The exclusive set is hardcoded in Python**, while the group names live in
  JSON data. Adding an exclusive group means editing both, and a typo in the
  data silently produces additive behaviour instead of an error.
- Group membership does not constrain which *fixtures* a scene may touch.
  Nothing stops a `sfeer` scene from writing Performer channels and fighting
  with `main`; the grouping is a UI and selection concept only.
- `aanuit` (`Alles Aan` / `Alles Uit`) overlaps every other group's fixtures by
  design. Activating `Alles Aan` does not deactivate the main or achtergrond
  layers, so the button highlights can suggest a state that the output
  contradicts.
- Group names are in mixed Dutch and English, matching the scene names the
  operator uses. Internally consistent, but jarring next to English code.

## Alternatives considered

- **A `mode` field per scene** (`exclusive` / `additive`) instead of a
  hardcoded set. More flexible and data-driven; rejected as premature for five
  groups, but it is the obvious fix if the hardcoded set becomes a nuisance.
- **Group definitions as a first-class object in `config.json`**, carrying
  display label, order, and exclusivity together. Cleaner, and would remove the
  Python/JSON split. Deferred to avoid a config migration.
- **No groups; free-form layering.** Simplest to implement, but pushes the
  "don't pick two background colours" rule onto the operator during a show.
