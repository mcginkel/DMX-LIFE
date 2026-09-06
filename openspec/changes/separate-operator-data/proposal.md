## Why

`app/config.json` lives inside the code repository and is the file the running
application writes to. Those two roles are incompatible.

Deployment is `ssh` to the venue Raspberry Pi followed by `git checkout`. The
moment an operator saves a scene there, the working tree is dirty, and the next
deployment either refuses to proceed or discards the change. The scenes are the
show; the repository is the software. Replacing one currently means losing the
other.

Nothing has been lost yet only because the system is not in production. It
will be, and the loss would be a Sunday's work discovered on a Sunday.

The same conflation blocks anything else worth doing with operator data. There
is no single artifact that *is* the show, so there is nothing to back up, sync
between the venue and home, or hand to a new installation. Separating the
shipped default from the live data is the precondition for all of it.

## What Changes

- The application reads and writes its configuration in an operator data
  directory outside the repository, resolved from `DMXLIFE_DATA_DIR` and
  defaulting to `~/dmx-life-show/`.
- `app/config.json` remains in the repository and keeps its current content,
  but changes role: it becomes a read-only seed, copied into the data
  directory the first time the application starts with no configuration
  there. The application never writes to it again. **BREAKING** for anyone
  who edits `app/config.json` expecting the running app to pick it up.
- The daily snapshots and the `.bak` file that `atomic-config-writes` and
  `add-daily-config-backup` produce follow the configuration into the data
  directory, so operator data is wholly contained in one place.
- Deploying by `git checkout` no longer touches operator data, in either
  direction: a deployment cannot destroy scenes, and scene edits cannot
  block a deployment.
- The PyInstaller bundle keeps shipping the seed, not live data.
- `README.md` documents where operator data lives, how to point at a
  different directory, and how to move an existing installation's data.

## Capabilities

### New Capabilities

None. This changes where configuration lives, not what the system does with
it.

### Modified Capabilities

- `configuration-persistence`: the specification currently describes durability
  and atomicity of "the configuration file" without saying where it lives or
  distinguishing it from the copy shipped with the software. It gains
  requirements covering the separation of shipped defaults from operator data,
  seeding on first run, and independence from software deployment. The existing
  atomicity, durability, retention and snapshot requirements are unchanged in
  substance and continue to apply to the operator data file.

## Impact

- Affected code: `app/__init__.py` (`CONFIG_FILE` resolution, seeding on
  startup), `app/config_manager.py` (backup and snapshot paths derive from the
  configuration's directory), `dmx-life.spec` (the bundled `config.json` is a
  seed), `start.sh` (may pass `DMXLIFE_DATA_DIR` through), `README.md`.
- Affected data: none destructively. An existing `app/config.json` is copied,
  not moved, so an installation that has not yet been migrated keeps working
  from the seed until the copy happens.
- Deployment: the venue Pi needs its data directory populated once. After
  that, `git checkout` is safe indefinitely.
- Enables, but does not implement: syncing show data between the venue and
  home (`sync-show-data-via-git`), and any per-scene file layout
  (`per-scene-files`). Both operate on the data directory this change
  establishes.
- Does not change the configuration's *format* - only its location and the
  distinction between seed and live data.
