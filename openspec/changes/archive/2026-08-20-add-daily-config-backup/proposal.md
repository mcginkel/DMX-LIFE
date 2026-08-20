## Why

`atomic-config-writes` already keeps `config.json.bak` — the version
immediately before the *last* write. That protects against one bad write,
but not against a session of several small, individually-reasonable changes
that add up to something the operator didn't want: by the time that's
noticed, `.bak` has already been overwritten by whatever came after the
mistake.

A once-a-day snapshot, taken lazily before the first write of a new day and
kept alongside every other day's snapshot, gives a genuine history to fall
back into - "how things were on any given day" - not just the most recent
morning.

## What Changes

- Before any write to `config.json`, if no snapshot exists for today's date,
  copy the current on-disk file to `backups/config-<YYYY-MM-DD>.json` first.
  Subsequent writes the same day are no-ops for this mechanism - one
  snapshot per day, taken from whatever the config looked like before that
  day's first change.
- Every day's snapshot is kept. Creating today's snapshot never touches a
  previous day's - the collection grows by one file per day the
  configuration actually changed.
- No restore functionality. Each snapshot is a plain file an operator can
  inspect or copy back manually; the application never reads any of them.
- Snapshotting is best-effort: a failure to write the snapshot (permissions,
  disk full) is logged but does not block the actual configuration save.
  The safety net is not allowed to become a new way to fail a real change.

## Non-goals

- **Automatic pruning of old snapshots.** Every day's file is kept
  indefinitely. At the file sizes involved (tens of KB each) this isn't a
  practical disk-space concern; a retention cap can be added later if it
  ever becomes one, without breaking this design.
- **Restore functionality** (UI, endpoint, or CLI to roll back to a
  snapshot). The operator copies a file back by hand if they ever need to;
  nothing in the application reads any `backups/config-<date>.json`.
- **Replacing or changing `atomic-config-writes`'s `.bak` mechanism.** That
  protects the single most recent write; this protects the start of the
  day. Different retention windows, different purposes, both kept.
- **Managing the pre-existing manually-created backup files** already in
  `backups/` from earlier work this session (`config.json.bak.<timestamp>-
  <label>`). Different naming pattern, out of this feature's scope - it
  only manages files matching its own `config-<date>.json` pattern.

## Capabilities

### Modified Capabilities
- `configuration-persistence`: adds a new requirement for the daily
  snapshot; no existing requirement's behavior changes.

## Impact

- Affected code: `app/config_manager.py` (`write()` gains the snapshot
  check), `.gitignore` (already covers `backups/`, confirm the new filename
  pattern is included).
- Assumption recorded here for review: snapshot lives in `backups/`
  (already exists, already gitignored, already the home for every manual
  backup taken this session) rather than alongside `config.json` in `app/`.
