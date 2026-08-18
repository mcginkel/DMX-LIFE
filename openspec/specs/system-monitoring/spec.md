# System Monitoring Specification

## Purpose

Defines what the operator can see about the system's own state — whether the
Art-Net link is alive, which scenes are active, and what values are actually on
the wire. When the lights do not respond, this is what distinguishes a network
fault from a patching mistake.

## Requirements

### Requirement: Connection status indicator

The system SHALL display the Art-Net connection state in the interface and
refresh it periodically without operator action.

#### Scenario: Connected state is shown

- **WHEN** Art-Net frames are being transmitted successfully
- **THEN** the interface indicates that the link is connected

#### Scenario: Disconnected state is shown

- **WHEN** transmission is failing
- **THEN** the interface indicates that the link is disconnected

#### Scenario: Status refreshes automatically

- **WHEN** the operator leaves a page open
- **THEN** the connection indicator updates periodically to reflect the current
  state

### Requirement: DMX value monitor

The system SHALL provide an on-demand view of current DMX channel values,
showing each channel's value and highlighting channels that are non-zero.

#### Scenario: Opening the monitor

- **WHEN** the operator opens the DMX monitor
- **THEN** current channel values are displayed and refreshed periodically

#### Scenario: Closing the monitor stops polling

- **WHEN** the operator closes the DMX monitor
- **THEN** the interface stops requesting DMX values

#### Scenario: Monitor is offered only where it is usable

- **WHEN** the viewport is too narrow to display the channel grid usefully
- **THEN** the monitor is not offered

### Requirement: Active scene reporting

The system SHALL report which scenes are currently active alongside DMX values,
so the operator can correlate the output with the selected looks.

#### Scenario: Monitor names the active scenes

- **WHEN** one or more scenes are active
- **AND** the operator views the DMX monitor
- **THEN** the active scene names are displayed

#### Scenario: No scenes active

- **WHEN** no scenes are active
- **THEN** the monitor indicates that none are active

### Requirement: Bounded value reporting

The system SHALL report DMX values only up to the highest channel claimed by the
active layers, rather than always returning the full universe, to keep the
polling payload small.

#### Scenario: Reporting stops at the highest used channel

- **WHEN** the active layers claim channels only up to a given address
- **THEN** the reported value list extends no further than that address
