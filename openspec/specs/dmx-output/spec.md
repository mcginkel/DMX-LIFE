# DMX Output Specification

## Purpose

Defines how the system drives physical lighting fixtures over Art-Net: the
continuous output stream, the crossfade between looks, immediate output for
previewing, and how connectivity to the Art-Net node is tracked.

## Requirements

### Requirement: Continuous Art-Net output

The system SHALL transmit the current 512-channel frame continuously at
approximately 30 frames per second from a single background thread, whether or
not the values have changed.

#### Scenario: Output continues while idle

- **WHEN** no scene has been activated for several minutes
- **THEN** the system continues transmitting the current frame at ~30 fps

#### Scenario: Single output thread

- **WHEN** the DMX controller is started more than once
- **THEN** only one output thread exists

#### Scenario: Output survives an unreachable node

- **WHEN** the Art-Net node cannot be reached
- **THEN** the output thread continues running
- **AND** transmission resumes automatically once the node is reachable again

### Requirement: Crossfade on scene change

The system SHALL fade from the current frame to a newly composed frame over a
fixed 3-second duration, interpolating each channel, and SHALL set every channel
exactly to its target value when the fade completes.

#### Scenario: Values move gradually

- **WHEN** a scene is activated that changes a channel from 0 to 255
- **THEN** that channel passes through intermediate values rather than jumping

#### Scenario: Fade settles exactly on target

- **WHEN** a fade has run for its full duration
- **THEN** every channel equals the target value with no rounding residue

#### Scenario: A new fade supersedes one in progress

- **WHEN** a fade is in progress
- **AND** another scene is activated
- **THEN** a new fade begins from the values currently on the wire toward the
  new target

### Requirement: Immediate output for previewing

The system SHALL provide an immediate output path that sets and transmits a
frame without fading, for previewing a scene while editing it.

#### Scenario: Preview applies instantly

- **WHEN** the operator previews a scene from the editor
- **THEN** the supplied channel values are transmitted without a fade

#### Scenario: Preview cancels an in-progress fade

- **WHEN** a fade is in progress
- **AND** an immediate output is requested
- **THEN** the fade is cancelled and the immediate values take effect

### Requirement: Connection status tracking

The system SHALL track whether Art-Net frames are being transmitted
successfully, expose that status, and log only transitions between the connected
and disconnected states rather than logging every failed frame.

#### Scenario: Loss of connectivity is recorded once

- **WHEN** transmission begins failing
- **THEN** the status becomes disconnected with the error recorded
- **AND** a single warning is logged rather than one per frame

#### Scenario: Recovery is recorded

- **WHEN** transmission succeeds after a period of failure
- **THEN** the status returns to connected
- **AND** the recovery is logged once

### Requirement: Runtime network reconfiguration

The system SHALL apply changed Art-Net settings without requiring a process
restart, stopping and restarting the output thread as needed.

#### Scenario: Applying new settings

- **WHEN** the Art-Net address, universe, packet size or refresh rate is changed
- **THEN** subsequent frames are transmitted using the new settings
- **AND** output resumes without restarting the application

### Requirement: Frame integrity

The system SHALL transmit frames of exactly 512 channels with values in the
range 0–255, and SHALL reject buffers that do not meet this shape.

#### Scenario: Malformed buffer is rejected

- **WHEN** a buffer that is not 512 bytes is supplied for output
- **THEN** the system raises an error rather than transmitting it
