# ADR-0001: JSON file as the system of record

- **Status:** Accepted
- **Date:** 2026-08-18 (documented retroactively)

## Context

DMX Life needs to persist three kinds of state: Art-Net network settings, the
fixture patch, and the saved scenes. The application is a single-operator tool
that runs on one machine on a local network, typically started before a show
and stopped afterwards. There is exactly one writer (the operator, through the
web UI) and the total data volume is small — tens of fixtures and a few dozen
scenes.

## Decision

Store all persistent state in a single JSON file, `app/config.json`, read and
written in full by `ConfigManager`. No database, no migration framework, no
schema versioning.

Every write is a full-file rewrite: read the whole document, mutate the
in-memory dictionary, serialise it back with `json.dump(..., indent=4)`.

## Consequences

**Good:**

- The entire system state is one human-readable file. It can be inspected with
  a text editor, diffed in git, copied to another machine, or hand-edited to
  recover from a UI bug.
- Backups are `cp`. Version history is git.
- No database process to install, run, or keep alive on the show machine.
- Scenes can be generated programmatically by writing JSON directly, which is
  how the Daslight-derived scenes were imported.

**Bad:**

- **No concurrency control.** Two simultaneous writes will lose one of them.
  Acceptable today because there is one operator, but any multi-user feature
  breaks this assumption.
- **No atomic writes.** `write()` truncates the file before writing. A crash
  or power loss mid-write leaves a corrupt, unparseable config and the
  application will fail to start.
- **No schema validation.** A malformed hand-edit is only discovered at
  runtime, potentially mid-show.
- Full-file rewrites mean scene saves get slower as the file grows. With
  512-value channel arrays per scene (see [ADR-0008](0008-scenes-as-full-channel-arrays.md))
  the file is already ~200 KB.

**Mitigation not yet implemented:** writing to a temporary file and using
`os.replace()` for an atomic swap would remove the corruption risk cheaply.

## Alternatives considered

- **SQLite.** Gives atomicity and concurrent-read safety, and ships with
  Python. Rejected because it makes the state opaque — no git diffs, no
  hand-editing, no trivially copyable config — for a concurrency problem this
  application does not currently have.
- **One file per scene.** Reduces rewrite cost and diff noise. Rejected as
  premature; it complicates the config-loading path for a file size that is
  not yet a real problem.
