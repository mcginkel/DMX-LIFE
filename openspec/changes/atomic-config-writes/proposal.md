# Write configuration atomically

## Why

`ConfigManager.write()` opens `app/config.json` with mode `'w'`, which truncates
the file to zero bytes before any new content is written:

```python
with open(self.config_file, 'w') as f:
    json.dump(config, f, indent=4)
```

Between the truncation and the completed write, the file on disk is empty or
partial. If the process is killed, the machine loses power, or the disk fills
during that window, the result is an unparseable `config.json` — and since it
holds every fixture and every scene ([ADR-0001](../../../docs/adr/0001-json-file-as-system-of-record.md)),
that is the entire show configuration.

`read()` re-raises on failure and `create_app()` calls it during startup, so a
truncated file means the application will not start. The recovery path is
restoring from git or a backup, which is not something to discover fifteen
minutes before an event.

The window is small but not negligible. The file is roughly 200 KB
([ADR-0008](../../../docs/adr/0008-scenes-as-full-channel-arrays.md)) and every
scene save, fixture edit and network change rewrites all of it.

## What changes

- Write to a temporary file in the same directory, flush it, and `os.replace()`
  it over the target. `os.replace` is atomic on POSIX and Windows, so a reader
  sees either the old file or the new one, never a partial one.
- `fsync` the temporary file before replacing, so the content is durable before
  the rename makes it visible.
- Keep the previous version as `config.json.bak` so a bad write can be undone
  without reaching for git.

## Non-goals

- Changing the storage format or moving to a database — ADR-0001 stands.
- Concurrent-write locking. There is one operator; the failure this addresses is
  interruption, not contention.
- Schema validation of the loaded file. Worth doing, but a separate concern.

## Impact

- Affected specs: `configuration-persistence` (new capability)
- Affected code: `app/config_manager.py`
- The temporary file must be created in the same directory as the target, since
  `os.replace` is only atomic within a filesystem.
