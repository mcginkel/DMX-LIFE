## MODIFIED Requirements

### Requirement: Per-fixture participation

The system SHALL let the operator choose which channels a scene claims, at
the granularity of an individual channel, and SHALL record that choice by
writing exactly the claimed channels into the scene's stored channel map -
including channels left at their default value - so that scene recall drives
only those channels.

Choosing participation for a whole fixture SHALL remain a single action, and
the system SHALL show, for each fixture, whether all, none, or only some of
its channels are claimed.

A scene whose claimed channels do not align to whole fixtures SHALL be
presented as it is stored and SHALL survive being opened and saved without
its set of claimed channels changing.

#### Scenario: Selecting participating fixtures

- **WHEN** the operator selects a fixture for a scene and saves it
- **THEN** every channel of that fixture is written into the scene's channel
  map, including channels left at zero

#### Scenario: Non-participating fixtures are left alone

- **WHEN** a scene selects only some fixtures
- **THEN** channels belonging to the other fixtures do not appear in that
  scene's channel map and are not driven by that scene

#### Scenario: Reopening a scene reconstructs the selection

- **WHEN** the operator reopens a saved scene for editing
- **THEN** each channel present in the scene's channel map is shown as
  claimed, and each channel absent from it is shown as not claimed

#### Scenario: Claiming part of a fixture

- **WHEN** the operator claims some but not all channels of a fixture and
  saves the scene
- **THEN** only the claimed channels of that fixture are written into the
  scene's channel map
- **AND** the fixture is shown as partially claimed rather than as fully
  selected or unselected

#### Scenario: A partially claimed scene survives a round trip

- **WHEN** a scene claims only some channels of a fixture
- **AND** the operator opens it in the editor and saves it without changing
  anything
- **THEN** the scene's set of claimed channels is unchanged

#### Scenario: Releasing a channel removes it from the scene

- **WHEN** the operator marks a previously claimed channel as not claimed and
  saves the scene
- **THEN** that channel no longer appears in the scene's channel map
- **AND** that channel is no longer driven by that scene, falling back to
  whatever other active layers define for it

#### Scenario: A claimed channel holding zero is preserved

- **WHEN** a scene claims a channel whose value is zero
- **THEN** that channel is written into the map with the value zero rather
  than omitted
