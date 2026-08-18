# Remove dead code and committed cruft

## Why

The repository carries a meaningful amount of code that nothing executes. It is
not harmful at runtime, but it actively misleads anyone reading the project —
including AI assistants working from the repository, which is how at least one
of these files keeps resurfacing in searches.

Inventory, all verified as unreferenced:

| Item | Size | Evidence |
|---|---|---|
| `app/dmx_controller_old.py` | 433 lines | No module imports it. Superseded by the split into `config_manager` / `scene_manager` / `dmx_controller_class` ([ADR-0012](../../../docs/adr/0012-app-factory-with-module-singletons.md)). |
| `lib/config.js`, `lib/dmxController.js`, `lib/fixture.js` | 0 bytes each | Empty files from an abandoned design iteration. |
| `app/utils/__init__.py`, `app/utils/filters.py` | 31 lines each | Byte-identical duplicates of each other. Neither is imported; `current_year` comes from a context processor in `app/__init__.py`. |
| `.DS_Store` | 6 KB | macOS metadata, committed to git. |
| `from flask.cli import F` in `app/models/fixture.py` | 1 line | Unused import of a private helper; an IDE autocomplete accident. |

`app/dmx_controller_old.py` is the most costly of these: it is a plausible-looking
433-line implementation of the same functionality, so a reader can easily spend
time in the wrong file, and it still references `MAX_SCENES` with the old limit.

## What changes

- Delete `app/dmx_controller_old.py`.
- Delete the three empty files in `lib/` and the directory if it is then empty.
- Delete `app/utils/` entirely, both files.
- Remove `.DS_Store` from version control and add it to `.gitignore`.
- Remove the unused import from `app/models/fixture.py`.

## Non-goals

- Refactoring any live code. This change removes only files and one import line
  that nothing references.
- Touching `design/prompt.txt` or the other design documents. They are historical
  records, not dead code.

## Impact

- Affected specs: none — no observable behaviour changes.
- Affected code: `app/dmx_controller_old.py`, `lib/`, `app/utils/`,
  `app/models/fixture.py`, `.gitignore`.
- Removed files remain recoverable from git history.
