# Tasks: write configuration atomically

## 1. Atomic write

- [ ] 1.1 In `ConfigManager.write()`, serialise to a temporary file created in
      the same directory as the target (`tempfile.NamedTemporaryFile(dir=...)`
      or `config.json.tmp`).
- [ ] 1.2 Flush and `os.fsync()` the temporary file before closing it.
- [ ] 1.3 Move the existing file to `config.json.bak` if present.
- [ ] 1.4 `os.replace()` the temporary file over `config.json`.
- [ ] 1.5 Remove the temporary file if any step fails, leaving the original
      untouched.

## 2. Startup diagnostics

- [ ] 2.1 In `ConfigManager.read()`, catch parse failures and raise an error
      naming the file, the parse problem, and the existence of
      `config.json.bak`.

## 3. Housekeeping

- [ ] 3.1 Add `app/config.json.bak` and `app/config.json.tmp` to `.gitignore`.

## 4. Verify

- [ ] 4.1 Saving a scene still persists correctly and the app reloads it.
- [ ] 4.2 After a save, `config.json.bak` holds the previous content.
- [ ] 4.3 Simulate failure by making the directory read-only: the write fails,
      `config.json` is unchanged and still parseable.
- [ ] 4.4 Interrupt a write (kill the process during a save loop) repeatedly;
      `config.json` is always parseable afterwards.
- [ ] 4.5 Corrupt `config.json` deliberately and confirm startup reports the
      file, the reason, and the backup — then restore it.
- [ ] 4.6 Network settings and fixture edits still save.

## 5. Notes

- [ ] 5.1 The temporary file must be on the same filesystem as the target, or
      `os.replace` is not atomic. Creating it in the same directory guarantees
      this.
