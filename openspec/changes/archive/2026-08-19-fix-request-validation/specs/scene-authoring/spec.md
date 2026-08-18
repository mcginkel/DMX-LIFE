## MODIFIED Requirements

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

## ADDED Requirements

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
