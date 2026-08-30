## MODIFIED Requirements

### Requirement: Per-fixture participation

The system SHALL let the operator choose which fixtures participate in a
scene via a per-fixture selection, and SHALL record that choice by writing
every channel of each selected fixture into the scene's stored channel map -
including channels left at their default value - so that scene recall
affects only those fixtures and the selection can be reconstructed later
from which channels the map contains.

#### Scenario: Selecting participating fixtures

- **WHEN** the operator selects a subset of fixtures for a scene and saves it
- **THEN** every channel of each selected fixture is written into the
  scene's channel map, including channels left at zero

#### Scenario: Non-participating fixtures are left alone

- **WHEN** a scene selects only some fixtures
- **THEN** channels belonging to the other fixtures do not appear in that
  scene's channel map and are not driven by that scene

#### Scenario: Reopening a scene reconstructs the selection

- **WHEN** the operator reopens a saved scene for editing
- **THEN** each fixture whose channels are present in the scene's channel
  map is shown as selected

### Requirement: Channel value validation

The system SHALL validate that supplied channel data is a map of channel
number to integer value, with channel numbers in the range 1-512 and values
in the range 0-255, before applying it to DMX output, and SHALL reject
anything else with a client error.

#### Scenario: Value above the permitted range

- **WHEN** a request supplies a channel value greater than 255
- **THEN** the system responds with a client error
- **AND** no unhandled error occurs

#### Scenario: Non-numeric channel value

- **WHEN** a request supplies a channel value that is not an integer
- **THEN** the system responds with a client error
- **AND** no unhandled error occurs

#### Scenario: Channel number out of range

- **WHEN** a request supplies a channel number outside 1-512
- **THEN** the system responds with a client error
- **AND** no unhandled error occurs

#### Scenario: Valid channel data is accepted

- **WHEN** a request supplies a map of channel numbers in 1-512 to integer
  values in 0-255
- **THEN** the request is processed normally
