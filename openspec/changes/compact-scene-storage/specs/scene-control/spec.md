## REMOVED Requirements

### Requirement: Fixture-scoped channel application

**Reason**: This requirement and "Sparse overlay application" existed only
because storing a scene's channels as a full-length array couldn't
distinguish "channel deliberately set to zero" from "channel this scene has
no opinion about" - so two different composition rules were needed
depending on whether `enabledFixtures` was empty. A `{channel: value}` map
makes presence itself the signal, removing the need for either rule as
written. See `compact-scene-storage`'s proposal for why.

**Migration**: No operator action needed. Existing scenes are converted
automatically on load - a fixture whose full range was previously copied
(non-empty `enabledFixtures`) becomes a map with every one of that
fixture's channels present as explicit keys, zeros included. Validated
against all 18 scenes in the real config and 242 realistic layer
combinations: byte-identical output to the pre-migration behavior.

### Requirement: Sparse overlay application

**Reason**: The other half of the same split - see above.

**Migration**: No operator action needed. A scene that previously used the
sparse-overlay path (empty `enabledFixtures`) becomes a map containing only
its non-zero channels, which is exactly what that path already selected.
Output is unchanged.

## ADDED Requirements

### Requirement: Sparse channel application

The system SHALL apply a scene's channels by writing exactly the channels
present in its stored channel map, using each entry's value as stored -
including a stored zero - and SHALL leave every channel absent from that map
untouched by that layer.

#### Scenario: A present zero is written

- **WHEN** a scene's channel map contains an entry with value 0
- **THEN** that channel is set to 0 in the frame

#### Scenario: An absent channel is left alone

- **WHEN** a channel does not appear in a scene's channel map
- **THEN** that channel is not modified by that layer, regardless of what
  value it holds from other active layers or from being previously unset

#### Scenario: A layer touches only its own claimed channels

- **WHEN** a scene's channel map contains entries for some channels of a
  fixture, and another active layer also drives that fixture
- **THEN** only the channels present in the first scene's map are
  overwritten by it
- **AND** the remaining channels of that fixture keep whatever the other
  active layer defines for them
