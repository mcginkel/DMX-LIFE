## Context

Templates have no shared base (`no {% extends %}` anywhere) - each of the
five HTML files renders its own footer independently. `app/__init__.py`
already has one context processor, `inject_year()`, that injects a value
computed once and available to every template without each view passing it
explicitly - the same shape this needs.

`dmx-life.spec` (PyInstaller) controls exactly which files end up inside a
packaged build via its `datas` list. Anything not listed there is invisible
to the frozen app at runtime, even though it's present in the source tree.

See proposal.md - Why for the motivation.

## Goals / Non-Goals

**Goals:**
- Reuse the existing `inject_year()` pattern exactly - no new mechanism.
- Make the PyInstaller packaging gap impossible to miss (it's easy to add a
  root-level file and forget the `.spec` needs to know about it too).

**Non-Goals:** see proposal.md.

## Decisions

### A plain `VERSION` text file at repo root, read once at startup

Read in `create_app()`, stored on `app.config['VERSION']`, exposed via a
context processor - not re-read per-request. The version can't change while
the process is running (a new version means a new release, which means a
restart), so re-reading on every request would just be wasted I/O with no
behavioral benefit.

Alternative considered: a Python constant (e.g. `app/__init__.py`'s
`__version__ = "1.0.0"`). Rejected - a plain text file is editable and
readable by any future release tooling (a shell script in the tag-and-zip
process, CI if it ever exists) without importing the Flask app or parsing
Python source.

### Missing/unreadable file falls back to `"unknown"`, caught at read time

The read is wrapped in a try/except at startup (file missing, unreadable,
empty). Consistent with this app's existing posture elsewhere (e.g. the
daily-backup change's swallow-and-log approach) - a cosmetic feature must
never be able to block the app from starting or serving pages.

### `dmx-life.spec` must list `VERSION` explicitly

PyInstaller's `datas` list is the only thing that determines what's inside
a frozen build; a file present in the repo but absent from `datas` simply
isn't there at runtime, and the missing-file fallback (showing "unknown")
would mask that mistake rather than fail loudly during development. Adding
`('VERSION', '.')` to `datas` is a one-line, explicit fix addressed in
tasks.md, not something to catch after the fact.

## Risks / Trade-offs

- **Someone forgets to bump `VERSION` before tagging.** → Not solved by
  software; it's a step in the same manual release process that already
  exists for tagging and zipping. Out of scope per proposal.md's non-goals
  (no verification that `VERSION` matches the git tag).
- **Packaged build silently shows "unknown" if `dmx-life.spec` isn't
  updated.** → Mitigated by making the `datas` entry an explicit task and a
  verification step (build once, confirm the packaged app shows the real
  version, not the fallback).
