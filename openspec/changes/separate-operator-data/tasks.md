## 0. Before starting

- [ ] 0.1 Back up `app/config.json` on this machine. Standing practice for any
      change that touches configuration.

## 1. Resolve the operator data location

- [ ] 1.1 Resolve the operator data directory in `app/__init__.py` from
      `DMXLIFE_DATA_DIR`, defaulting to `~/dmx-life-show/`, expanding `~` and
      any environment variables in the supplied value.
- [ ] 1.2 Set `CONFIG_FILE` to `<data dir>/config.json` instead of the path
      next to `app/__init__.py`.
- [ ] 1.3 Create the data directory if it does not exist, failing with a clear
      message naming the path if it cannot be created.
- [ ] 1.4 Log the resolved operator data location at startup, so an operator
      can tell which data the running instance is using.

## 2. Seed from the shipped default

- [ ] 2.1 On startup, when the data directory has no `config.json`, copy the
      shipped `app/config.json` into it.
- [ ] 2.2 When a configuration is already present, do not read the shipped
      default at all.
- [ ] 2.3 Log which of the two paths was taken - seeded from default, or used
      existing.
- [ ] 2.4 Seed from a directory that exists but is empty, not only from an
      absent one (a freshly cloned data repository is the case that matters).
- [ ] 2.5 Confirm no code path writes to the shipped `app/config.json`.

## 3. Derived files follow the configuration

- [ ] 3.1 Confirm `ConfigManager`'s `.bak` path derives from the configuration
      path, so it lands in the data directory.
- [ ] 3.2 Confirm the daily snapshot directory resolves to `backups/` inside
      the data directory rather than next to `app/`.
- [ ] 3.3 `ConfigManager._ensure_config_exists()` must not fight the seeding in
      section 2 - decide which one creates a missing file and make the other
      defer to it.

## 4. Deployment and packaging

- [ ] 4.1 Confirm `git checkout` in the repository no longer touches operator
      data, and that a modified operator configuration does not leave the
      working tree dirty.
- [ ] 4.2 `dmx-life.spec` keeps shipping `app/config.json` as a seed; verify a
      built bundle resolves its data directory to the user's home rather than
      to a path inside the bundle.
- [ ] 4.3 Decide whether `start.sh` should pass `DMXLIFE_DATA_DIR` through, and
      do so if it should.

## 5. Documentation

- [ ] 5.1 Document in `README.md` where operator data lives, how to override it
      with `DMXLIFE_DATA_DIR`, and the one-time copy that moves an existing
      installation's data.
- [ ] 5.2 Note the service-manager caveat: a unit running with a different
      `HOME` resolves `~` elsewhere, so a managed deployment should set
      `DMXLIFE_DATA_DIR` explicitly.

## 6. Verify

- [ ] 6.1 Fresh start with no data directory: it is created, seeded, and the
      application comes up with the seed's fixtures and scenes.
- [ ] 6.2 Start with existing operator data: it is used unchanged, and the
      shipped default is untouched.
- [ ] 6.3 Save a scene, then confirm the shipped `app/config.json` is
      byte-identical to what it was before the save.
- [ ] 6.4 Save a scene, then confirm `git status` in the repository is clean.
- [ ] 6.5 `config.json.bak` and `backups/config-<date>.json` are created inside
      the data directory, not next to `app/`.
- [ ] 6.6 Point `DMXLIFE_DATA_DIR` at a different directory and confirm the
      application uses it and reports it at startup.
- [ ] 6.7 Copy the data directory to a second location, start against it, and
      confirm the show is identical - the directory is genuinely self-contained.
