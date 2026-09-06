## Why

Scenes address the rig by DMX channel number. A scene says `{111: 255}`, which
means "whatever is patched at 111". Change a fixture's start address in Fixture
Setup and every scene that drove it now drives whatever else sits there - the
scenes still load, the application reports no error, and the wrong lamps light
up.

This is the same failure mode the project already fixed one level down.
`fix-fixture-link-references` replaced positional `linked_to` indices with
fixture names because reordering the patch silently corrupted every link
(ADR-0010). Scenes have the identical coupling, with more data at stake, and it
has not been addressed.

The robust fix would be to store scenes symbolically - fixture plus channel
role rather than raw address - so repatching costs nothing. That is a large
change to the data model and the editor, and it is insurance against a risk the
operator rates as low: the rig is stable, and address changes are occasional.

There is a cheaper fix that removes the silence, which is the part that
actually hurts. The application is the one making the change. At the moment a
fixture's address is edited, it holds both the old address and the new one. It
can rewrite the affected scenes itself.

## What Changes

- Changing a fixture's start address offers to rewrite every scene entry that
  falls within that fixture's old range, moving it to the corresponding channel
  in the new range.
- Removing a fixture offers to drop that fixture's channels from every scene
  that claims them, rather than leaving scenes driving addresses that no longer
  belong to anything.
- Changing a fixture's type, where the channel count or channel meanings
  differ, is reported as needing a decision rather than being migrated
  automatically. The tool cannot know that channel 3 of one model means what
  channel 3 of another does.
- The operator confirms before anything is rewritten, and is shown what will
  change - which scenes, how many channels each - before deciding.
- The rewrite is logged before and after, following the pattern of the existing
  migrations.
- Adding a fixture needs no migration: addresses that were not previously
  claimed cannot be referenced by an existing scene.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `fixture-configuration`: editing the patch currently has no stated
  relationship to scene data. It gains requirements covering what happens to
  scenes when a fixture's addressing changes or a fixture is removed, and the
  requirement that the operator sees and confirms the consequence first.

## Impact

- Affected code: `app/views/setup.py` (the fixture save path computes and
  applies the consequence), `app/static/js/fixtures.js` and the fixtures
  template (presenting the consequence and taking confirmation),
  `app/config_manager.py` if the rewrite is expressed there.
- Affected data: scenes are rewritten - deliberately, with confirmation, and
  only in response to a rig edit the operator just made.
- Explicitly does **not** change the scene storage format. Scenes stay
  address-based; this makes address changes safe rather than making addresses
  unnecessary.
- What this does not protect against: an address change made by editing the
  operator data directly rather than through Fixture Setup. The safety comes
  from the edit passing through the application, which is where both sides of
  the mapping exist.
