## Why

Once operator data syncs between the venue Pi and the operator's laptop
(`sync-show-data-via-git`), the shape of the stored data decides how often a
merge needs a human.

Everything currently lives in one `config.json` that `ConfigManager.write()`
rewrites in full on every save. Adding or deleting a scene shifts every line
after it, which a line-based merge reads as a large change even though one
scene was touched. Two people editing unrelated scenes in the same week can
therefore produce a conflict that has nothing to do with their edits meeting.

A conflict in a single JSON file is also the worst possible artifact: conflict
markers make the file unparseable, so the application will not start until a
person resolves it by hand.

Splitting the store so that each scene is its own file makes the file layout
match the editing granularity. Two people editing different scenes cannot
conflict at all, and a conflict that does happen means what it says - the same
scene was edited in both places.

## What Changes

- Scenes are stored one file per scene under `scenes/` in the operator data
  directory, rather than as an array inside `config.json`.
- The fixture patch and the output settings move to their own files alongside
  it, so each file has a single subject.
- Scene filenames are derived from the scene name, so a diff and a `git log`
  name the scene that changed. Names that collide after slugification get a
  disambiguating suffix.
- Migration on read, following the pattern used by every previous format
  change: an existing single `config.json` is split on load, logged, and
  written back in the new layout on the next save.
- **BREAKING** at the data-layout level for anything reading the operator data
  directly. Nothing outside this codebase does.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `configuration-persistence`: the atomicity and durability requirements are
  written in terms of "the configuration file", singular. With several files
  they need to state what a reader is guaranteed to observe when a write spans
  more than one of them, and what the retained-previous-version and daily
  snapshot requirements cover.

## Impact

- Affected code: `app/config_manager.py` (reading, writing and migrating a
  directory rather than a file), and anything that assumes `read()` returns one
  document - the views already treat it as a single dict, so the interface can
  stay.
- Affected data: the operator data directory is restructured in place on first
  save after the change.
- **This change is deliberately not scheduled yet.** It is an ergonomic
  improvement to merges, not a correctness fix: with the venue on its own
  branch and merges performed on the operator's laptop, a bad merge cannot
  reach the venue. The right time to decide is after a few weeks of real
  merges, when there is evidence about how often unrelated edits actually
  collide. The proposal exists so the reasoning is not lost; it should not be
  implemented before that evidence exists.
- Open question for that decision: atomicity across several files is weaker
  than across one. A crash mid-write could leave scenes from two compositions
  on disk. Whether that matters in practice, and what guarantee replaces the
  current single-rename one, is the main design work this change would need.
