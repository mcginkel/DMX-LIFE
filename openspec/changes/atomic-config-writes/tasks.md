# Tasks: write configuration atomically

## 1. Atomic write

- [x] 1.1 In `ConfigManager.write()`, serialise to a temporary file created in
      the same directory as the target (`tempfile.NamedTemporaryFile(dir=...)`
      or `config.json.tmp`). Used the fixed `config.json.tmp` name rather than
      `NamedTemporaryFile`, since a fixed name makes the crash-recovery state
      predictable (task 4.4) and there's only ever one writer.
- [x] 1.2 Flush and `os.fsync()` the temporary file before closing it.
- [x] 1.3 Move the existing file to `config.json.bak` if present.
- [x] 1.4 `os.replace()` the temporary file over `config.json`.
- [x] 1.5 Remove the temporary file if any step fails, leaving the original
      untouched. Also handles the narrower case where the *backup* rename
      succeeded but the final replace then failed: restores it before
      re-raising, so `config.json` is never left missing.

## 2. Startup diagnostics

- [x] 2.1 In `ConfigManager.read()`, catch parse failures and raise an error
      naming the file, the parse problem, and the existence of
      `config.json.bak`.

## 3. Housekeeping

- [x] 3.1 Add `app/config.json.bak` and `app/config.json.tmp` to `.gitignore`.

## 4. Verify

- [x] 4.1 Saving a scene still persists correctly and the app reloads it.
- [x] 4.2 After a save, `config.json.bak` holds the previous content. Verified
      it holds the exact prior values (94/48/0), not the new ones.
- [x] 4.3 Simulate failure by making the directory read-only: the write fails,
      `config.json` is unchanged and still parseable. Also confirmed no
      leftover `.tmp` file survives the failure.
- [x] 4.4 Interrupt a write (kill the process during a save loop) repeatedly;
      `config.json` is always parseable afterwards. Ran 60 iterations of
      `kill -9` at randomized 1-8ms offsets into a tight write loop, against
      an isolated scratch copy — 60/60 left `config.json` parseable.
- [x] 4.5 Corrupt `config.json` deliberately and confirm startup reports the
      file, the reason, and the backup — then restore it. Tested both via
      `ConfigManager.read()` directly (with and without a `.bak` present) and
      via a real `create_app()` startup against the actual `app/config.json`;
      restored immediately after, confirmed byte-identical to a pre-test
      snapshot.
- [x] 4.6 Network settings and fixture edits still save. (The fixture
      round-trip reordered JSON keys via Flask's `jsonify` — cosmetic only,
      same values — so `config.json` was reset to the committed version
      afterwards rather than left with an unrelated diff.)

## 5. Notes

- [x] 5.1 The temporary file must be on the same filesystem as the target, or
      `os.replace` is not atomic. Creating it in the same directory guarantees
      this. Confirmed: `tmp_path = f"{self.config_file}.tmp"` is a sibling of
      the target by construction.
