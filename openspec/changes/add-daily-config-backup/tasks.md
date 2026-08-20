## 1. Snapshot mechanism

- [ ] 1.1 In `ConfigManager.write()`, before the existing atomic-write
      sequence, check whether `backups/config-<today's date>.json` exists.
- [ ] 1.2 If it doesn't, and `self.config_file` currently exists, copy the
      current on-disk file to `backups/config-<today's date>.json`
      (`shutil.copy2`, not the temp+rename mechanism - see design.md).
- [ ] 1.3 Before writing the new snapshot, remove any other file matching
      the strict `config-YYYY-MM-DD.json` pattern in `backups/` - exactly
      one snapshot at a time. Do not touch files that don't match this
      exact pattern (e.g. the existing `config.json.bak.<timestamp>-
      <label>` files from earlier manual backups).
- [ ] 1.4 Wrap the whole snapshot step in try/except: log any failure via
      `current_app.logger`, and let the real write proceed regardless.
- [ ] 1.5 Ensure `backups/` is created if it doesn't exist yet.

## 2. Housekeeping

- [ ] 2.1 Confirm `.gitignore`'s existing `backups/` entry covers the new
      `config-<date>.json` filename pattern (it should, being a directory
      ignore - verify, don't assume).

## 3. Verify

- [ ] 3.1 First config write of a fresh day creates
      `backups/config-<date>.json` containing the pre-write content.
- [ ] 3.2 A second write the same day does not create or modify another
      snapshot file.
- [ ] 3.3 Simulate a new day (adjust the check or the file's mtime) and
      confirm a new snapshot is created and the previous day's file is
      removed - exactly one `config-<date>.json` file exists afterward.
- [ ] 3.4 Pre-existing manually-named backup files in `backups/` are left
      untouched by the cleanup step.
- [ ] 3.5 Make `backups/` unwritable (or otherwise force the snapshot copy
      to fail) and confirm the real configuration write still succeeds,
      with the failure logged.
- [ ] 3.6 Confirm no new endpoint, UI element, or code path reads
      `backups/config-<date>.json` back - restore is not implemented, per
      the non-goal.
