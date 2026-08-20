## Why

`atomic-config-writes` already keeps `config.json.bak` — the version
immediately before the *last* write. That protects against one bad write,
but not against a session of several small, individually-reasonable changes
that add up to something the operator didn't want: by the time that's
noticed, `.bak` has already been overwritten by whatever came after the
mistake.

A once-a-day snapshot, taken lazily before the first write of a new day,
gives a longer-horizon fallback — "how things were this morning" — without
turning into a growing archive nobody asked for.

## What Changes

- Before any write to `config.json`, if no snapshot exists for today's date,
  copy the current on-disk file to `backups/config-<YYYY-MM-DD>.json` first.
  Subsequent writes the same day are no-ops for this mechanism - one
  snapshot per day, taken from whatever the config looked like before that
  day's first change.
- Exactly one snapshot is kept at a time. Creating today's snapshot removes
  any previous day's dated snapshot. This is deliberately not a history -
  see proposal Non-goals.
- No restore functionality. The snapshot is a plain file an operator can
  inspect or copy back manually; the application never reads it.
- Snapshotting is best-effort: a failure to write the snapshot (permissions,
  disk full) is logged but does not block the actual configuration save.
  The safety net is not allowed to become a new way to fail a real change.

## Non-goals

- **Keeping a history of daily snapshots.** Explicitly one file, replaced
  daily - not `config-2026-08-18.json`, `config-2026-08-19.json`, ... piling
  up forever.
- **Restore functionality** (UI, endpoint, or CLI to roll back to the
  snapshot). The operator copies the file back by hand if they ever need it;
  nothing in the application reads `backups/config-<date>.json`.
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
