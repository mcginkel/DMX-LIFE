## Context

`ConfigManager.write()` is the single choke point for every config.json
mutation - network settings, fixtures, scenes, and any migration write-back
(fixture links today, scene channels if `compact-scene-storage` lands) all
funnel through it. That makes it the one place this needs to hook in,
without touching any of the call sites above it.

## Goals / Non-Goals

**Goals:**
- One snapshot per calendar day, taken lazily, kept indefinitely - a real
  history to fall back into, not just the most recent morning.
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

### The existence check is a single, exact filename - no deletion, no glob

There's no cleanup step at all - every snapshot this feature creates stays
untouched forever, so the only file-matching operation is the "does today's
snapshot already exist" check, and that's a single exact path
(`backups/config-<YYYY-MM-DD>.json`), not a pattern match over the
directory. Nothing in this feature enumerates or interprets `backups/`'s
contents, which is also why the pre-existing manually-named
`config.json.bak.<timestamp>-<label>` files from earlier this session are
automatically unaffected - this code never looks at them.

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
- **Unbounded growth.** A snapshot every day the config changes, forever,
  with no pruning. → Accepted, not mitigated: at tens of KB per snapshot
  this is years away from mattering, and adding a retention cap later (e.g.
  "keep the last N") is a small, backward-compatible addition to this same
  code path whenever it's actually worth doing - not designed in now on
  spec.

## Migration Plan

Additive only - no existing data or behavior changes. First write after
deploying this creates the first snapshot; nothing to migrate.
