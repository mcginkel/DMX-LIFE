## Context

`ConfigManager.write()` is the single choke point for every config.json
mutation - network settings, fixtures, scenes, and any migration write-back
(fixture links today, scene channels if `compact-scene-storage` lands) all
funnel through it. That makes it the one place this needs to hook in,
without touching any of the call sites above it.

## Goals / Non-Goals

**Goals:**
- One snapshot, taken lazily, replaced daily - not a growing archive.
- Never let the safety net itself become a reason a real save fails.

**Non-Goals:** see proposal.md.

## Decisions

### Hook at the very top of `write()`, before the atomic-write sequence

The snapshot needs to capture the file *as it currently stands on disk* -
i.e. before this write's temp-file/rename dance touches it at all. It runs
first, as its own step, then the existing atomic-write logic proceeds
completely unchanged below it.

### A plain copy, not the same atomic-rename mechanism as the main write

`atomic-config-writes`'s temp+rename exists because writing *new, freshly
serialised* content into the live path has a real interrupted-write window.
Copying an *already-valid, already-on-disk* file to a new path doesn't share
that failure mode the same way - worst case on interruption is simply "no
snapshot got made today," which is exactly the pre-existing state, not
corruption. A plain `shutil.copy2` is enough; reusing the heavier mechanism
here would be solving a risk that isn't present.

### Identify "this feature's files" by a strict date pattern, not a loose glob

Retention cleanup (deleting yesterday's snapshot when today's is created)
must only ever touch files matching `config-YYYY-MM-DD.json` exactly - not
a loose `config-*.json` glob, which could catch a differently-named file a
person happens to create by hand. This is the same reasoning as the
proposal's non-goal about not touching the pre-existing manually-named
`config.json.bak.<timestamp>-<label>` files: this feature manages only the
files it itself creates, identified unambiguously.

### Failure is caught, logged, and swallowed - never propagated

The snapshot step is wrapped so that any exception (permissions, disk full,
whatever) is logged and discarded before proceeding to the real write. An
operator saving a network setting mid-show should never be blocked by a
failed backup attempt for a feature they may not even know exists.

## Risks / Trade-offs

- **Silent failure** is the natural cost of "never block the real write."
  A daily backup that's been silently failing for weeks gives false
  confidence. → Mitigated by logging every failure (visible in `nohup.out`
  even if nobody's watching for it); a health-check surfacing this is
  future scope, not needed for the safety net itself to be worth having.
- **Date is server-local time.** Fine for a single-machine, single-operator
  tool; would need revisiting if this ever ran distributed.

## Migration Plan

Additive only - no existing data or behavior changes. First write after
deploying this creates the first snapshot; nothing to migrate.
