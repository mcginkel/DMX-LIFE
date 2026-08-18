# Add an automated test suite

## Why

There are no automated tests. Every change is verified by starting the server
and clicking through the interface, which is slow, easy to skip, and only covers
what the tester remembers to try.

The cost is already visible in this codebase:

- The scene editor's "Add Scene" button was disabled for a period after the
  scene limit was raised, because `/setup/api/config` never returned
  `MAX_SCENES`. A single API-shape test would have caught it.
- `DELETE /setup/api/config/scenes` raises `KeyError` on a missing name, and the
  guard meant to prevent that has never worked.
- The `linked_to` values in `config.json` contain self-references that the UI is
  supposed to make impossible.

None of these are subtle. They survived because nothing checks.

The layered scene model is the strongest argument for tests: composing a DMX
frame from a set of active layers is a pure function of that set, which makes it
exactly the kind of logic that is cheap to test and unpleasant to verify by
hand. Confirming that toggling a layer off restores what was underneath
currently requires activating scenes in a browser and reading channel values out
of an API.

The seven specifications in `openspec/specs/` were written as testable
scenarios. They are the test plan.

## What changes

- Add `pytest` as a development dependency, with a `requirements-dev.txt`.
- Add unit tests for `SceneManager` — layering, group exclusivity, toggling,
  fixture-scoped versus sparse application — driven by a fixture config rather
  than the real `config.json`.
- Add unit tests for `ConfigManager` against a temporary directory.
- Add API tests using Flask's test client, covering the documented success and
  rejection cases for each endpoint.
- Add focused tests for `DMXController`'s interpolation arithmetic, with the
  socket stubbed and no thread running.
- Document how to run them in `README.md`.

## Non-goals

- Browser or end-to-end tests. The value-per-effort is much lower than the
  layers above, and the interface changes more often than the logic.
- Testing `stupidartnet` itself, or asserting on real network traffic.
- Chasing a coverage percentage. The target is the behaviour in the specs, not a
  number.
- Retrofitting tests for code that `remove-dead-code` deletes.

## Impact

- Affected specs: none — this verifies existing specifications rather than
  changing behaviour.
- Affected code: new `tests/` directory, `requirements-dev.txt`, `README.md`.
- Sequencing: best done after `fix-request-validation`, so the API tests assert
  the corrected behaviour rather than encoding today's 500s.
