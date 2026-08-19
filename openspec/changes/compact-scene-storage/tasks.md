## 0. Before starting

- [ ] 0.1 Back up `app/config.json`. Same practice as every prior migration
      this session - this rewrites every scene.

## 1. Migration

- [ ] 1.1 In `ConfigManager.read()`, detect scenes whose `channels` is still
      a list (old shape) and convert to a `{channel: value}` map: non-empty
      `enabledFixtures` → every claimed fixture's full channel range as
      explicit entries (zeros included); empty `enabledFixtures` → only the
      non-zero entries.
- [ ] 1.2 Convert JSON's string keys to `int` at this single boundary - the
      in-memory representation is `{int: int}`, never `{str: int}`.
- [ ] 1.3 Drop `enabledFixtures` from the migrated in-memory scene dict -
      it's not carried forward.
- [ ] 1.4 Log a before/after summary of the migration (channel count before
      vs. after per scene), same pattern as `_migrate_fixture_links`.
- [ ] 1.5 Idempotent: a scene whose `channels` is already a map is left
      untouched on read.

## 2. SceneManager

- [ ] 2.1 Collapse `_apply_scene` to the single rule: for each `(channel,
      value)` in the active scene's map, write it to the buffer. Remove the
      `enabledFixtures`-branching and the fixture-list lookup entirely.
- [ ] 2.2 Confirm `_rebuild_buffer` and layer-ordering (activation order,
      later wins) are otherwise unchanged.
- [ ] 2.3 `save_scene`/`delete_scene` pass the map straight through - no
      `enabledFixtures` parameter needed for new saves.

## 3. API surface

- [ ] 3.1 Rewrite `find_invalid_channel` (or its replacement) in
      `app/views/setup.py` to validate a map: keys parse as integers in
      1-512, values are integers in 0-255 (booleans still explicitly
      rejected, same reasoning as today).
- [ ] 3.2 Update `save_scene_endpoint`/`test_scene_endpoint` to pass the
      validated map through instead of a list.
- [ ] 3.3 Update `app/dmx_controller.py`'s `test_scene(channels)` to accept
      a map and write only the present entries into its preview buffer.

## 4. Frontend (`app/static/js/scenes.js`)

- [ ] 4.1 On save/test, build the payload as a map: for each *enabled*
      fixture, write every one of its channels (from its sliders) as
      explicit entries, including ones at 0. Unchecked fixtures contribute
      no entries.
- [ ] 4.2 On loading a scene for editing, derive which fixtures are
      "enabled" (checkbox state) from whether their channel numbers appear
      in the scene's map, rather than reading a stored `enabledFixtures`
      list.
- [ ] 4.3 Populate slider values from the map, defaulting to each channel's
      type-defined default for channels absent from the map (matches
      today's behavior for a freshly-enabled fixture).

## 5. Verify

- [ ] 5.1 Every one of the 18 real scenes migrates and activates correctly
      - compare DMX output against a pre-migration baseline for at least
        the layer combinations explored earlier (main × achtergrond × sfeer
        × extra).
- [ ] 5.2 `config.json` size after migration matches the projected ~67%
      reduction, within a reasonable margin.
- [ ] 5.3 Creating a new scene through the editor, with a mix of enabled
      and disabled fixtures, produces a map containing exactly the enabled
      fixtures' channels.
- [ ] 5.4 Reopening that scene for editing shows the correct checkboxes
      checked, with no stored `enabledFixtures` field involved.
- [ ] 5.5 A scene that deliberately zeroes a fixture (an "Uit" scene)
      still zeroes it correctly when active alongside other layers.
- [ ] 5.6 Malformed channel payloads (out-of-range channel number,
      out-of-range value, non-integer, boolean) are all rejected with a
      client error, not a 500.
- [ ] 5.7 An old-shape `config.json` (arrays + `enabledFixtures`) loads,
      migrates, and behaves identically to before - confirmed via the
      logged before/after migration summary.
