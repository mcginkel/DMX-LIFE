## Context

Two facts about how this system is actually run shape the design.

Deployment is `ssh` to the venue Raspberry Pi followed by `git checkout`. It is
not a package install or an image flash - the working tree *is* the
installation. Anything the application writes into that tree is in the path of
the next deployment.

The Pi and the operator's laptop both run the application against their own
data, and that data is edited on both. Reconciling them is the subject of
`sync-show-data-via-git`, not this change, but it sets a constraint here: the
operator data location has to be somewhere a person can reasonably clone a git
repository into and look at, not somewhere the operating system hides.

## Goals / Non-Goals

**Goals:**
- A deployment can never destroy operator data, and operator data can never
  block a deployment.
- One directory that wholly contains "the show", so it can be copied, synced
  or handed to another installation as a unit.
- A fresh installation starts usable without manual setup.

**Non-Goals:**
- Changing the configuration format. The file's contents are exactly what they
  are today; only its location and role change. `per-scene-files` is where a
  layout change would be considered.
- Implementing backup, sync or multi-show support. This change makes them
  possible; it does not do them.
- Migrating an existing installation automatically from the old location. See
  "Existing installations" below for why that is deliberate.

## Decisions

### `~/dmx-life-show/`, not an OS convention directory

The operator data location is resolved from `DMXLIFE_DATA_DIR`, defaulting to
`~/dmx-life-show/`.

The conventional choice would be `~/Library/Application Support/DMX-LIFE/` on
macOS and `~/.local/share/dmx-life/` on Linux. Rejected, for a specific
reason: this directory is going to become a git repository that the operator
clones, pulls, inspects and merges by hand. A path that differs per platform,
contains spaces, and is hidden from the file manager makes every one of those
operations worse. The same path on the Pi and the laptop is worth more here
than platform convention.

`DMXLIFE_DATA_DIR` exists so a deployment that disagrees can say so, and so
tests can point somewhere disposable - the same shape as `DMXLIFE_HOST` and
the credential variables.

### The shipped file keeps its path and gains a role

`app/config.json` stays where it is, tracked, with its current content. It
stops being the file the application writes and becomes the seed copied on
first run.

**Alternative considered:** renaming it to `app/config.default.json` to make
the read-only role obvious in the filename. Rejected on the operator's
instruction to keep it, and the loss is mitigated by the fact that nothing in
the code writes to it any more - the role is enforced by behaviour, not by
naming. Worth revisiting if anyone is ever confused by it.

A consequence worth stating: the seed currently contains a specific venue's
rig and scenes. That is intentional for this installation - a fresh checkout
should come up driving the real rig - but it means the seed is not a neutral
example. If the project is ever handed to someone else, replacing the seed
with a minimal example is a separate decision.

### Seeding is copy-on-absence, checked at startup

On startup, if the operator data location has no configuration, the shipped
default is copied into it. If one is present, the shipped default is not read
at all.

The check is for the *configuration file*, not the directory: a directory that
exists but is empty (a freshly cloned data repository, for instance) seeds
normally.

**Alternative considered:** seeding lazily on first read. Rejected - it makes
the startup log silent about which of the two paths was taken, and the
application already resolves credentials and version at startup, so this fits
the existing shape.

### Derived files follow the configuration

`ConfigManager` currently derives `config.json.bak` from the configuration path
and computes the daily snapshot directory as `../backups` relative to it. Both
already derive from the configuration's location rather than being independent
constants, so pointing the configuration at the data directory carries them
along - `backups/` becomes a sibling of the configuration inside the data
directory rather than a sibling of `app/`.

This is what makes "copy the directory and you have the show" true, and it is
also what makes the data repository self-contained for `sync-show-data-via-git`.

### Existing installations are not migrated automatically

An installation that already has data in `app/config.json` is not moved to the
new location by the software.

This looks like an omission and is deliberate. There are exactly two
installations - the laptop and the Pi - and the operator has shell access to
both. An automatic migration would have to guess whether a tracked
`app/config.json` that differs from `HEAD` represents real operator work or a
stale edit, and guessing wrong destroys the show. A documented one-line copy,
performed once per machine by someone who knows which data matters, is safer
than any heuristic.

The seeding behaviour means doing nothing is also safe: an un-migrated machine
seeds from the tracked file and comes up with exactly the data it had before.

## Risks / Trade-offs

- **The Pi is deployed before its data directory is populated.** It would seed
  from the tracked `app/config.json`, which is the laptop's configuration -
  correct rig, but possibly not the venue's latest scenes. → Populate the Pi's
  data directory as part of the one-time migration, before the first
  deployment that includes this change.
- **`~` is ambiguous under a service manager.** A `systemd` unit or a launch
  agent may run with a different `HOME` than the interactive user, seeding a
  second empty configuration somewhere unexpected. → Reporting the resolved
  location at startup makes this visible immediately rather than as mysteriously
  missing scenes; a deployment that uses a service manager should set
  `DMXLIFE_DATA_DIR` explicitly.
- **The PyInstaller bundle still ships `app/config.json`.** That remains
  correct - it is the seed - but the bundled application must resolve its data
  directory to the user's home, not to the bundle's internal path. → Verify on
  a built bundle, not only from source.

## Migration Plan

1. Land the change. Both machines keep working unchanged, seeding from the
   tracked file on first start.
2. On each machine, once: copy `app/config.json` to `~/dmx-life-show/config.json`
   before first start of the new version, so the live data - not the tracked
   seed - is what gets used.
3. Confirm from the startup log that the expected location is in effect, and
   that scenes and fixtures are intact in the interface.
4. Thereafter `git checkout` on the Pi touches only code.
5. Rollback: revert the commit. The old code reads `app/config.json`, which was
   copied rather than moved and is therefore still present and valid.
