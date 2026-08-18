# Scene Control Specification

## Purpose

Defines how an operator selects lighting looks during a show. Scenes behave as
independently toggleable layers organised into groups; the system composes the
active layers into the DMX frame that goes to the fixtures.

This is the capability the operator uses live, under time pressure, so its
behaviour must be predictable and reversible.

## Requirements

### Requirement: Scene toggling

The system SHALL treat scene activation as a toggle. Activating a scene that is
already active SHALL deactivate it.

#### Scenario: Activating an inactive scene

- **WHEN** the operator activates a scene that is not currently active
- **THEN** the scene is added to the set of active layers
- **AND** the response lists it among the active scenes

#### Scenario: Deactivating an active scene

- **WHEN** the operator activates a scene that is currently active
- **THEN** the scene is removed from the set of active layers
- **AND** the response omits it from the active scenes

#### Scenario: Unknown scene

- **WHEN** an activation request names a scene that does not exist
- **THEN** the system reports failure
- **AND** the set of active layers is unchanged

### Requirement: Exclusive group selection

The system SHALL define a set of exclusive groups — `main`, `achtergrond`,
`sfeer` and `aanuit` — within which at most one scene may be active. Activating
a scene in an exclusive group SHALL deactivate the group's currently active
member.

#### Scenario: Switching within an exclusive group

- **WHEN** `blauw/oranje` in group `main` is active
- **AND** the operator activates `rood/oranje`, also in group `main`
- **THEN** `blauw/oranje` becomes inactive
- **AND** `rood/oranje` becomes active

#### Scenario: Exclusivity does not cross groups

- **WHEN** `rood/oranje` in group `main` is active
- **AND** the operator activates `Blauw` in group `achtergrond`
- **THEN** both scenes are active simultaneously

### Requirement: Additive scene layering

The system SHALL treat any scene whose group is not an exclusive group —
including scenes with no group — as additive. An additive scene SHALL neither
deactivate nor be deactivated by scenes in other groups.

#### Scenario: Adding an overlay on top of a main scene

- **WHEN** a scene in group `main` is active
- **AND** the operator activates `extraLampSpreker` in group `extra`
- **THEN** both scenes are active
- **AND** the main scene remains active

### Requirement: Frame composition from active layers

The system SHALL rebuild the complete 512-channel DMX frame from zero on every
toggle by applying each active layer in activation order, oldest first. It SHALL
NOT patch the previously transmitted frame.

#### Scenario: Removing a layer restores what is underneath

- **WHEN** a main scene sets channel 40 to 228
- **AND** an overlay scene subsequently sets channel 40 to 255
- **AND** the operator deactivates the overlay
- **THEN** channel 40 returns to 228

#### Scenario: Removing the only claimant zeroes the channel

- **WHEN** exactly one active layer sets channel 34 to 223
- **AND** the operator deactivates that layer
- **THEN** channel 34 becomes 0

#### Scenario: Later layers win contested channels

- **WHEN** two active layers both claim the same channel
- **THEN** the value from the most recently activated layer is transmitted

### Requirement: Fixture-scoped channel application

When a scene lists one or more fixtures in `enabledFixtures`, the system SHALL
copy every channel in each named fixture's address range from the scene into the
frame, including channels whose value is zero, and SHALL leave channels outside
those fixtures untouched.

#### Scenario: Scene writes zeros within its own fixtures

- **WHEN** a scene enables a fixture and stores 0 for one of that fixture's
  channels
- **THEN** that channel is set to 0 in the frame

#### Scenario: Scene does not disturb fixtures it does not enable

- **WHEN** a scene enables only the Tribar fixtures
- **THEN** channels belonging to the Performer fixtures are unaffected by that
  layer

### Requirement: Sparse overlay application

When a scene's `enabledFixtures` is empty, the system SHALL apply only the
channels holding a non-zero value, ignoring fixture address boundaries.

#### Scenario: Overlay touches only its own channels

- **WHEN** a sparse scene stores non-zero values at channels 34, 36, 40, 47 and
  49
- **AND** those channels fall inside fixtures driven by another active layer
- **THEN** only those five channels are overwritten
- **AND** the remaining channels of those fixtures keep the other layer's values

### Requirement: Grouped scene presentation

The main page SHALL present scenes grouped by their `group` field, in a defined
display order, and SHALL render scenes whose group is unrecognised under a
catch-all section so that no configured scene is hidden.

#### Scenario: Groups are rendered in order

- **WHEN** the operator opens the main page
- **THEN** scene groups appear in the order `main`, `achtergrond`, `sfeer`,
  `aanuit`, followed by additive scenes

#### Scenario: Ungrouped scenes remain reachable

- **WHEN** a configured scene has no group or an unrecognised group
- **THEN** it is displayed under a catch-all section

### Requirement: Server-authoritative active state

The system SHALL hold the set of active scenes on the server and return it with
every activation response. The interface SHALL derive its indication of what is
active from that set rather than tracking it independently.

#### Scenario: Reload reflects true state

- **WHEN** scenes are active
- **AND** the operator reloads the main page
- **THEN** exactly those scenes are shown as active

#### Scenario: Highlighting follows the server

- **WHEN** an activation response is received
- **THEN** every scene button's active indication is set from the returned list
