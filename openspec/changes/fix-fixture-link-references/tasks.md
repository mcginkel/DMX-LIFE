# Tasks: repair and harden fixture link references

## 0. Before starting

- [ ] 0.1 Commit or back up `app/config.json`. The migration rewrites every
      `linked_to` value and is one-way.

## 1. Migration

- [ ] 1.1 In `ConfigManager`, convert integer `linked_to` values to master names
      on load.
- [ ] 1.2 Rule 1: an index pointing at a different fixture of the same type
      converts to that fixture's name.
- [ ] 1.3 Rule 2: an index pointing at the fixture itself is treated as
      off-by-one and resolved to `index - 1`, if that fixture is of the same
      type.
- [ ] 1.4 Rule 3: anything still unresolved becomes `null`, with a warning
      naming the fixture.
- [ ] 1.5 Log a before/after table of every conversion.

## 2. Verify the repair by eye

- [ ] 2.1 Confirm `Perf3`–`Perf6` resolve to `Perf2`.
- [ ] 2.2 Confirm `Par2`–`Par8` resolve to `Par1`.
- [ ] 2.3 Confirm `Sfeer rechts` resolves to `Sfeer Links`.
- [ ] 2.4 Review `Tribar3` and `Tribar4` with the operator — the stored data
      suggests a chain, which is not permitted, so their intended masters must
      be confirmed rather than inferred.

## 3. Server-side validation

- [ ] 3.1 Validate in `update_fixtures` that each link names an existing
      fixture.
- [ ] 3.2 Reject self-links.
- [ ] 3.3 Reject links to a fixture of a different type.
- [ ] 3.4 Reject links to a fixture that is itself linked.
- [ ] 3.5 Reject duplicate fixture names.

## 4. Frontend

- [ ] 4.1 Update `fixtures.js` to store and read link references by name.
- [ ] 4.2 Update `scenes.js` link lookups to match by name.
- [ ] 4.3 Remove the index-renumbering logic on deletion; clear links naming the
      deleted fixture instead.
- [ ] 4.4 Keep the existing client-side restrictions on the link dropdown.

## 5. Verify

- [ ] 5.1 Adjusting a `Perf2` slider propagates to `Perf3`–`Perf6`.
- [ ] 5.2 Adjusting a `Par1` slider propagates to `Par2`–`Par8`.
- [ ] 5.3 Deleting a fixture in the middle of the list leaves all other links
      pointing at the same masters.
- [ ] 5.4 A self-link posted directly to the API is rejected.
- [ ] 5.5 A duplicate fixture name is rejected.
- [ ] 5.6 An old config with integer links still loads and is converted.
- [ ] 5.7 Scene activation is unaffected — links do not touch DMX output.
