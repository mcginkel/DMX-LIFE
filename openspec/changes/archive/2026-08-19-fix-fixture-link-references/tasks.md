# Tasks: repair and harden fixture link references

## 0. Before starting

- [x] 0.1 Commit or back up `app/config.json`. The migration rewrites every
      `linked_to` value and is one-way. (Working tree was already committed;
      also took an explicit local backup in `backups/`.)

## 1. Migration

- [x] 1.1 In `ConfigManager`, convert integer `linked_to` values to master names
      on load.
- [x] 1.2 Rule 1: an index pointing at a different fixture of the same type
      converts to that fixture's name.
- [x] 1.3 Rule 2: an index pointing at the fixture itself is treated as
      off-by-one and resolved to `index - 1`, if that fixture is of the same
      type.
- [x] 1.4 Rule 3: anything still unresolved becomes `null`, with a warning
      naming the fixture. Implemented as two sub-cases: no valid target at
      all, and (not spelled out in the task text, but required to match the
      design's own worked example) a resolved target that is itself linked
      — a chain — which is caught in a dedicated validation pass. Without
      it, Perf4-6/Par3-8 would each resolve to the *broken* self-referential
      fixture (Perf3/Par2) rather than flattening to the real master
      (Perf2/Par1), and Tribar4 would silently resolve to Tribar3 despite
      the chain the design explicitly forbids.
- [x] 1.5 Log a before/after table of every conversion.

## 2. Verify the repair by eye

- [x] 2.1 Confirm `Perf3`–`Perf6` resolve to `Perf2`.
- [x] 2.2 Confirm `Par2`–`Par8` resolve to `Par1`.
- [x] 2.3 Confirm `Sfeer rechts` resolves to `Sfeer Links`.
- [x] 2.4 Review `Tribar3` and `Tribar4` with the operator — the stored data
      suggests a chain, which is not permitted, so their intended masters must
      be confirmed rather than inferred. Migration correctly resolves
      `Tribar3` to `Tribar2` and leaves `Tribar4` unlinked (chain rejected).
      Flagging to the user in the completion summary for confirmation of
      what `Tribar4` should link to, if anything — that's their call, not
      an inference the migration should make.

## 3. Server-side validation

- [x] 3.1 Validate in `update_fixtures` that each link names an existing
      fixture.
- [x] 3.2 Reject self-links.
- [x] 3.3 Reject links to a fixture of a different type.
- [x] 3.4 Reject links to a fixture that is itself linked.
- [x] 3.5 Reject duplicate fixture names.

Beyond the listed tasks: `update_fixtures` was also still using bare
`request.json` (no JSON-body-required guard) — flagged as this change's job
in `fix-request-validation`'s own completion summary, since it's the exact
endpoint this change already modifies for validation. Fixed alongside it
rather than leaving it half-done, using the same `get_json_object()`
pattern as every other endpoint.

## 4. Frontend

- [x] 4.1 Update `fixtures.js` to store and read link references by name.
      Also removed a `|| true` in `updateLinkOptions()` that permanently
      short-circuited its own "hasLinkedFixtures" filter — pre-existing dead
      code the index-to-name conversion made obvious; not something I went
      looking for.
- [x] 4.2 Update `scenes.js` link lookups to match by name.
- [x] 4.3 Remove the index-renumbering logic on deletion; clear links naming the
      deleted fixture instead.
- [x] 4.4 Keep the existing client-side restrictions on the link dropdown.
      Same-type filter, "master already has followers" disable, and
      "don't offer an already-linked fixture as a target" filter are all
      preserved, just name-keyed instead of index-keyed.

## 5. Verify

- [x] 5.1 Adjusting a `Perf2` slider propagates to `Perf3`–`Perf6`. Verified
      live in the browser: moved Perf2's Rood slider via a dispatched input
      event, confirmed Perf3/4/5/6 all followed to the same value.
- [x] 5.2 Adjusting a `Par1` slider propagates to `Par2`–`Par8`. Same method,
      confirmed Par2 and Par8 (both ends of the group).
- [x] 5.3 Deleting a fixture in the middle of the list leaves all other links
      pointing at the same masters. Deleted `Perf4` (index 3, mid-array) via
      the real API; `Perf3`/`Perf5`/`Perf6` still read `linked_to: "Perf2"`
      afterward, undisturbed. Then restored it.
- [x] 5.4 A self-link posted directly to the API is rejected. Also tested a
      chain (`Perf1` -> `Perf3`, where `Perf3` is itself linked) - rejected
      with "because it is itself linked".
- [x] 5.5 A duplicate fixture name is rejected.
- [x] 5.6 An old config with integer links still loads and is converted.
      Verified via a real `create_app()`/server startup against the actual
      `app/config.json`, not just the isolated unit test from section 1 -
      the migration log and the API response matched exactly.
- [x] 5.7 Scene activation is unaffected — links do not touch DMX output.
      Activated and deactivated a real scene via the API mid-verification;
      worked normally throughout.
