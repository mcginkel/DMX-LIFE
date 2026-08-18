# Tasks: remove dead code and committed cruft

## 1. Confirm each item is unreferenced

- [ ] 1.1 `grep -rn "dmx_controller_old" --include="*.py" .` returns no imports.
- [ ] 1.2 `grep -rn "utils" --include="*.py" app/` shows no import of
      `app.utils` or `NowExtension`.
- [ ] 1.3 No template references `lib/` assets.

## 2. Remove

- [ ] 2.1 Delete `app/dmx_controller_old.py`.
- [ ] 2.2 Delete `lib/config.js`, `lib/dmxController.js`, `lib/fixture.js`, and
      the `lib/` directory if empty.
- [ ] 2.3 Delete `app/utils/__init__.py` and `app/utils/filters.py`, and the
      `app/utils/` directory.
- [ ] 2.4 Remove the unused `from flask.cli import F` from
      `app/models/fixture.py`.
- [ ] 2.5 `git rm --cached .DS_Store` and add `.DS_Store` to `.gitignore`.

## 3. Verify

- [ ] 3.1 Application starts without import errors.
- [ ] 3.2 Main page renders and the footer year is still correct (confirms the
      context processor, not the deleted extension, supplies it).
- [ ] 3.3 Scene activation still works.
- [ ] 3.4 Fixture setup page still loads fixture types.
- [ ] 3.5 `git status` is clean and `.DS_Store` no longer tracked.

## 4. Follow-up

- [ ] 4.1 Update `.github/copilot-instructions.md`, which currently tells
      assistants not to modify `lib/`, `routes/` and `views/` as "legacy" — the
      first will no longer exist, and `app/views/` is very much live code.
