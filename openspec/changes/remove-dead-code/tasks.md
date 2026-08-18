# Tasks: remove dead code and committed cruft

## 1. Confirm each item is unreferenced

- [x] 1.1 `grep -rn "dmx_controller_old" --include="*.py" .` returns no imports.
- [x] 1.2 `grep -rn "utils" --include="*.py" app/` shows no import of
      `app.utils` or `NowExtension`.
- [x] 1.3 No template references `lib/` assets.

## 2. Remove

- [x] 2.1 Delete `app/dmx_controller_old.py`.
- [x] 2.2 Delete `lib/config.js`, `lib/dmxController.js`, `lib/fixture.js`, and
      the `lib/` directory if empty. Note: `lib/` was already git-ignored
      (boilerplate `lib/` pattern), so these were never committed — plain
      `rm`, not `git rm`. The proposal's "committed cruft" framing was
      slightly off for this item; flagged to the user.
- [x] 2.3 Delete `app/utils/__init__.py` and `app/utils/filters.py`, and the
      `app/utils/` directory.
- [x] 2.4 Remove the unused `from flask.cli import F` from
      `app/models/fixture.py`.
- [x] 2.5 `git rm --cached .DS_Store` and add `.DS_Store` to `.gitignore`.

## 3. Verify

- [x] 3.1 Application starts without import errors.
- [x] 3.2 Main page renders and the footer year is still correct (confirms the
      context processor, not the deleted extension, supplies it). Verified
      against the actual current year (2026).
- [x] 3.3 Scene activation still works.
- [x] 3.4 Fixture setup page still loads fixture types.
- [x] 3.5 `.DS_Store` no longer in `git ls-files`; the deletion is staged as
      expected (that's the change itself, not stray state).

## 4. Follow-up

- [x] 4.1 Update `.github/copilot-instructions.md`, which currently tells
      assistants not to modify `lib/`, `routes/` and `views/` as "legacy" — the
      first will no longer exist, and `app/views/` is very much live code.
      Fixed only this one line; the rest of that file's staleness (scene
      model, MAX_SCENES) is `refresh-architecture-docs`' job.
