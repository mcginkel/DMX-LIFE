# Scene Authoring Specification

## Purpose

Defines how an operator creates, edits, previews and deletes the lighting scenes
that are later recalled during a show. This is setup-time work, done before an
event rather than during one.

## Requirements

### Requirement: Scene creation and editing

The system SHALL allow an operator to create a named scene and to edit an
existing one, setting a value in the range 0–255 for each visible channel of
each participating fixture.

#### Scenario: Saving a new scene

- **WHEN** the operator names a scene and saves it with channel values
- **THEN** the scene is persisted and appears in the scene list

#### Scenario: Editing an existing scene

- **WHEN** the operator saves a scene using the name of an existing scene
- **THEN** the existing scene is replaced rather than duplicated

#### Scenario: Name is required

- **WHEN** a save is attempted without a scene name or without channel values
- **THEN** the system rejects the request and reports why

### Requirement: Per-fixture participation

The system SHALL let the operator choose which fixtures participate in a scene,
and SHALL record that choice with the scene so that scene recall affects only
those fixtures.

#### Scenario: Selecting participating fixtures

- **WHEN** the operator enables a subset of fixtures for a scene and saves it
- **THEN** the enabled fixture names are stored with the scene

#### Scenario: Non-participating fixtures are left alone

- **WHEN** a scene that enables only some fixtures is recalled
- **THEN** channels belonging to the other fixtures are not driven by that scene

### Requirement: Scene grouping

The system SHALL allow a scene to carry a group, and SHALL persist it so that
scene recall can apply the group's selection behaviour.

#### Scenario: Group is stored with the scene

- **WHEN** a scene is saved with a group
- **THEN** the group is persisted alongside its name, channels and fixtures

#### Scenario: Group is optional

- **WHEN** a scene is saved without a group
- **THEN** the scene is stored with no group and is treated as additive on recall

### Requirement: Scene preview

The system SHALL provide a preview that applies a scene's channel values to the
fixtures immediately, without a fade and without saving, so the operator can
judge the result while editing.

#### Scenario: Previewing uncommitted values

- **WHEN** the operator previews the scene currently being edited
- **THEN** the current slider values are output immediately
- **AND** the scene is not saved

### Requirement: Scene limit

The system SHALL enforce a maximum number of stored scenes, SHALL reject new
scenes beyond that limit, and SHALL expose the limit so the editor can show
remaining capacity and prevent an attempt that would fail.

#### Scenario: Limit is reported to the editor

- **WHEN** the editor loads configuration
- **THEN** the response includes the configured maximum scene count

#### Scenario: Creating beyond the limit is refused

- **WHEN** the number of stored scenes has reached the maximum
- **AND** the operator attempts to save a scene with a new name
- **THEN** the system refuses and reports that the limit is reached

#### Scenario: Editing at the limit is still allowed

- **WHEN** the number of stored scenes has reached the maximum
- **AND** the operator saves changes to an existing scene
- **THEN** the save succeeds

### Requirement: Scene deletion

The system SHALL allow a stored scene to be deleted, and SHALL remove it from
the active set if it was active. It SHALL reject a deletion request that does
not identify a scene by name, without raising an unhandled error.

#### Scenario: Deleting a scene

- **WHEN** the operator deletes a scene
- **THEN** it no longer appears in the scene list or in stored configuration

#### Scenario: Deleting an active scene

- **WHEN** the operator deletes a scene that is currently active
- **THEN** the scene is removed from the set of active layers

#### Scenario: Deletion request without a name

- **WHEN** a deletion request omits the scene name or supplies an empty one
- **THEN** the system responds with a client error stating that the name is
  required
- **AND** no unhandled error occurs

#### Scenario: Scene name matching a payload field name

- **WHEN** a deletion request names a scene whose name coincides with a field
  name in the request payload
- **THEN** the scene is deleted normally

### Requirement: Channel value validation

The system SHALL validate that supplied channel data is a list of integers in
the range 0–255 before applying it to DMX output, and SHALL reject anything else
with a client error.

#### Scenario: Value above the permitted range

- **WHEN** a request supplies a channel value greater than 255
- **THEN** the system responds with a client error
- **AND** no unhandled error occurs

#### Scenario: Non-numeric channel value

- **WHEN** a request supplies a channel value that is not an integer
- **THEN** the system responds with a client error
- **AND** no unhandled error occurs

#### Scenario: Valid channel data is accepted

- **WHEN** a request supplies channel values that are all integers in 0–255
- **THEN** the request is processed normally

### Requirement: Well-formed request bodies

The system SHALL reject requests whose body is absent or is not a JSON object
with a client error rather than an unhandled error.

#### Scenario: Missing request body

- **WHEN** a request that requires a JSON body supplies none
- **THEN** the system responds with a client error
