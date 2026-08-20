## 1. Snapshot mechanism

- [x] 1.1 In `ConfigManager.write()`, before the existing atomic-write
      sequence, check whether `backups/config-<today's date>.json` exists.
- [x] 1.2 If it doesn't, and `self.config_file` currently exists, copy the
      current on-disk file to `backups/config-<today's date>.json`
      (`shutil.copy2`, not the temp+rename mechanism - see design.md).
- [x] 1.3 Wrap the whole snapshot step in try/except: log any failure via
      `current_app.logger`, and let the real write proceed regardless.
- [x] 1.4 Ensure `backups/` is created if it doesn't exist yet.
- [x] 1.5 No deletion logic anywhere in this feature - every day's snapshot
      is permanent once written (see design.md - unbounded growth is an
      accepted trade-off, not something to work around here).

## 2. Housekeeping

- [x] 2.1 Confirm `.gitignore`'s existing `backups/` entry covers the new
      `config-<date>.json` filename pattern (it should, being a directory
      ignore - verify, don't assume).

## 3. Verify

- [x] 3.1 First config write of a fresh day creates
      `backups/config-<date>.json` containing the pre-write content.
- [x] 3.2 A second write the same day does not create or modify another
      snapshot file.
- [x] 3.3 Simulate a new day (adjust the check or the file's mtime) and
      confirm a *new* snapshot is created **and** the previous day's file is
      still present, unchanged - both `config-<date1>.json` and
      `config-<date2>.json` exist afterward.
- [x] 3.4 Pre-existing manually-named backup files in `backups/` are
      untouched (this feature never enumerates the directory, only checks
      one exact path, so this should hold trivially - confirm anyway).
- [x] 3.5 Make `backups/` unwritable (or otherwise force the snapshot copy
      to fail) and confirm the real configuration write still succeeds,
      with the failure logged.
- [x] 3.6 Confirm no new endpoint, UI element, or code path reads
      `backups/config-<date>.json` back - restore is not implemented, per
      the non-goal.
