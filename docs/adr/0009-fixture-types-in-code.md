# ADR-0009: Fixture types defined in Python code

- **Status:** Accepted
- **Date:** 2026-08-18 (documented retroactively)

## Context

Every DMX fixture model has its own channel layout — a 3-channel RGB par, a
4-channel dimmer-plus-RGB par, a 13-channel moving head. To build a usable
scene editor the application must know, for each patched fixture, how many
channels it occupies and what each one does.

The venue's rig uses a small, stable set of models: Performer 2000 (13ch tour
mode), Compac Par 18 Tri, ShowTec LEDPAR 56, plus generic RGB and single-dimmer
types.

## Decision

Define fixture types as a dictionary literal in
`app/models/fixture.py` — `FixtureType.TYPES` — keyed by display name. Each
type lists its channels in order, and each channel carries:

- `name` — the label shown in the editor (e.g. `Rood`, `Zoom kl->gr`).
- `default` — its default value.
- `visible` — whether the editor renders a slider for it.

The `visible` flag exists so that channels an operator should never touch
during a show (`Macro`, `Programma`, `Dimmersnelheid`) stay out of the way
without being removed from the fixture's channel count.

Adding a fixture model means editing this file and restarting.

## Consequences

**Good:**

- Channel layouts are version-controlled and reviewable alongside the code.
- No import/parse layer, no fixture-library file format, no UI for editing
  fixture profiles — all of which would be substantial work for a rig that
  changes maybe once a year.
- The `visible` flag keeps the scene editor uncluttered while preserving
  correct channel counts.

**Bad:**

- **Adding a fixture model requires a code change and a deploy.** A user cannot
  patch a newly hired fixture without editing Python, which contradicts the
  project's "built for non-technical users" goal.
- Channel names are in the operator's language (Dutch) inside otherwise English
  source, and are inconsistent across types (`Rood` in one type, `Red` in
  another).
- `channel_count` is stored redundantly on each patched fixture in
  `config.json` as well as being derivable from the type. Nothing enforces that
  the two agree; a mismatch would silently corrupt scene application.
- No relationship to any standard fixture library, so profiles cannot be shared
  or imported.

## Alternatives considered

- **Fixture profiles in `config.json`.** Editable without a deploy and needs no
  new file format. The natural next step if the rig starts changing; deferred
  because it also requires a profile-editing UI to be genuinely useful.
- **Import from the Open Fixture Library.** Thousands of ready-made profiles in
  a documented JSON format. Attractive long-term; rejected as a large
  integration for a five-model rig.
- **Import from Daslight `.ssl`/`.dvc` files.** Investigated when migrating the
  venue's scenes. The show file format is encrypted and undocumented, so this
  is not viable.
