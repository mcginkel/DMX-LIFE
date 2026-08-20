## Why

Releases are tagged and zipped manually - there's no CI, no build number, no
`git describe` available inside a PyInstaller-packaged build (it doesn't
carry `.git`). Without a version visible in the running app, "which build is
this" has no answer short of comparing file contents.

## What Changes

- A plain `VERSION` file at the repo root holds the current version string
  (e.g. `1.0.0`), edited by hand as part of the existing manual
  tag-and-zip release process - this change does not touch or automate that
  process, only adds somewhere for the app to read the number from.
- The version is read once at startup and injected into every page via a
  Flask context processor, the same mechanism already used for
  `current_year` (`app/__init__.py`'s `inject_year()`).
- Displayed in the footer of all five templates (`index.html` and the four
  `setup/*.html` pages), which already render `current_year` there - same
  place, same pattern, no new UI surface introduced.
- If `VERSION` is missing or unreadable, the app starts and renders
  normally, showing a placeholder ("unknown") instead of a real number
  rather than failing.

## Non-goals

- **Automated version bumping, changelog generation, or CI.** The
  maintained value is edited by hand, same as the git tag it's expected to
  match - this change only makes that number visible, not automated.
- **Deriving the version from git** (`git describe --tags` or similar) at
  runtime. Rejected outright: a PyInstaller-frozen build doesn't carry
  `.git`, so this would work in development and silently break (or need
  a fallback anyway) in the one context - a packaged release - where seeing
  the version matters most.
- **An API endpoint exposing the version.** Not requested - this is a
  screen-visible display, not a programmatic contract. Trivial to add later
  if ever needed.
- **Verifying the `VERSION` file matches the eventual git tag.** Keeping
  the two in agreement is the releaser's responsibility as part of the
  existing manual process, not something the app checks.

## Capabilities

### New Capabilities
- `version-display`: the application has and shows its own version number.

## Impact

- Affected code: new `VERSION` file at repo root, `app/__init__.py` (read
  it once, add a context processor), all five templates (append version to
  the existing footer line), `dmx-life.spec` (must list `VERSION` in
  `datas` or a packaged build silently loses it - see design.md).
- Assumptions recorded here for review: version lives in the footer
  (already present on every page, already the home for the one other piece
  of "about this build" info - the copyright year); source is a plain text
  file at repo root rather than a Python constant, so it's readable by any
  future release tooling without needing to import the app.
