# Fixture Configuration Specification

## Purpose

Defines how the physical lighting rig is described to the system: which fixtures
exist, what model each one is, where each sits in the DMX address space, and
which fixtures move together when scenes are edited.

## Requirements

### Requirement: Fixture patching

The system SHALL allow an operator to define fixtures, each with a name, a
fixture type, and a starting DMX channel, and SHALL persist them.

#### Scenario: Adding a fixture

- **WHEN** the operator supplies a name, type and starting channel
- **THEN** the fixture is stored with a channel count derived from its type
- **AND** it becomes available for use in scenes

#### Scenario: Fixtures persist across restarts

- **WHEN** the application is restarted
- **THEN** the previously defined fixtures are still present

### Requirement: Fixture type catalogue

The system SHALL provide a catalogue of fixture types, each defining an ordered
list of channels with a name and a default value, and SHALL expose the catalogue
so the editor can render appropriate controls.

#### Scenario: Retrieving available types

- **WHEN** the editor requests the fixture type catalogue
- **THEN** the system returns the available type names

#### Scenario: Retrieving a type's channel layout

- **WHEN** the editor requests the details of a fixture type
- **THEN** the system returns its channels in order with names and defaults

#### Scenario: Unknown type falls back safely

- **WHEN** channel details are requested for a type that is not in the catalogue
- **THEN** the system returns the generic single-channel layout rather than
  failing

### Requirement: Hidden channels

The system SHALL mark selected channels of a fixture type as not visible, and
the scene editor SHALL omit controls for them while still counting them toward
the fixture's channel footprint.

#### Scenario: Control channels are hidden from the editor

- **WHEN** a fixture type marks channels such as macro or program-speed as not
  visible
- **THEN** the editor renders no sliders for them
- **AND** the fixture still occupies its full channel range in the address map

### Requirement: Fixture linking

The system SHALL allow a fixture to be linked to another fixture of the same
type, designating that other fixture as its master, so that edits to the master
propagate to its linked fixtures.

#### Scenario: Linked fixtures follow the master while editing

- **WHEN** the operator adjusts a channel on a master fixture in the scene
  editor
- **THEN** the corresponding channel on each fixture linked to it receives the
  same value

#### Scenario: Linking is restricted to matching types

- **WHEN** the operator attempts to link a fixture to one of a different type
- **THEN** the link is rejected

#### Scenario: Chains and self-links are prevented

- **WHEN** the operator attempts to link a fixture to itself, or to a fixture
  that already has fixtures linked to it
- **THEN** the link is rejected

### Requirement: Link maintenance on deletion

When a fixture is deleted, the system SHALL clear links that pointed at it and
SHALL adjust the stored references of fixtures whose position changed, so that
no link points at the wrong fixture.

#### Scenario: Links to a deleted fixture are cleared

- **WHEN** a fixture that other fixtures were linked to is deleted
- **THEN** those fixtures are left unlinked

#### Scenario: References are corrected after removal

- **WHEN** a fixture earlier in the list is deleted
- **THEN** links referring to fixtures after it are adjusted to keep pointing at
  the same fixtures

### Requirement: Channel conflict detection

The system SHALL detect when a fixture's channel range overlaps that of an
existing fixture and SHALL warn the operator before accepting it.

#### Scenario: Overlapping patch is flagged

- **WHEN** the operator adds a fixture whose channel range overlaps an existing
  fixture
- **THEN** the system names the conflicting fixtures and asks for confirmation
  before saving

### Requirement: DMX address map

The system SHALL present a visual map of the DMX address space showing which
channels are occupied and by which fixture.

#### Scenario: Occupied channels are identifiable

- **WHEN** the operator views the fixture setup page
- **THEN** channels assigned to a fixture are visually distinguished from free
  channels
- **AND** the owning fixture can be identified from the map
