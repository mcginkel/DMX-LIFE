## 1. Version source

- [ ] 1.1 Create `VERSION` at the repo root containing a single version
      string (e.g. `1.0.0`, no trailing newline needed but harmless if
      present).
- [ ] 1.2 In `app/__init__.py`, read `VERSION` once during `create_app()`,
      wrapped in try/except so a missing or unreadable file falls back to
      the string `"unknown"` instead of raising.
- [ ] 1.3 Store the resolved value on `app.config['VERSION']`.

## 2. Template injection

- [ ] 2.1 Add a context processor alongside the existing `inject_year()`
      (same `create_app()` scope) that exposes the resolved version to
      every template, e.g. `app_version`.
- [ ] 2.2 Append the version to the footer line in `index.html`, next to
      the existing `{{ current_year }}` text.
- [ ] 2.3 Do the same in `setup/index.html`, `setup/network.html`,
      `setup/fixtures.html`, and `setup/scenes.html` - each footer edited
      individually since there is no shared base template.

## 3. Packaging

- [ ] 3.1 Add `('VERSION', '.')` to the `datas` list in `dmx-life.spec` so
      a packaged build carries the file.

## 4. Verify

- [ ] 4.1 Run the dev server and load each of the five pages; confirm the
      version from `VERSION` appears in the footer on all of them.
- [ ] 4.2 Temporarily rename/remove `VERSION`, restart the server, and
      confirm every page still loads normally and shows "unknown" instead
      of a real version; restore the file afterward.
- [ ] 4.3 Change the value in `VERSION` and restart; confirm the displayed
      number updates accordingly.
- [ ] 4.4 Build the app via `dmx-life.spec` (PyInstaller) and confirm the
      packaged executable shows the real version, not the "unknown"
      fallback - proves the `datas` entry actually works, not just that
      the source tree has the file.
