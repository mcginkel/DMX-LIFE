## MODIFIED Requirements

### Requirement: Continuous Art-Net output

The system SHALL transmit the current 512-channel frame continuously at
approximately 30 frames per second from a single background thread, whether or
not the values have changed, regardless of which output backend is active.

#### Scenario: Output continues while idle

- **WHEN** no scene has been activated for several minutes
- **THEN** the system continues transmitting the current frame at ~30 fps

#### Scenario: Single output thread

- **WHEN** the DMX controller is started more than once
- **THEN** only one output thread exists

#### Scenario: Output survives an unreachable node

- **WHEN** the active backend cannot be reached (an unreachable Art-Net node,
  a disconnected USB interface, or equivalent for the active backend)
- **THEN** the output thread continues running
- **AND** transmission resumes automatically once the backend is reachable
  again

### Requirement: Connection status tracking

The system SHALL track whether frames are being transmitted successfully
through the active backend, expose that status, and log only transitions
between the connected and disconnected states rather than logging every
failed frame.

#### Scenario: Loss of connectivity is recorded once

- **WHEN** transmission through the active backend begins failing
- **THEN** the status becomes disconnected with the error recorded
- **AND** a single warning is logged rather than one per frame

#### Scenario: Recovery is recorded

- **WHEN** transmission succeeds after a period of failure
- **THEN** the status returns to connected
- **AND** the recovery is logged once

### Requirement: Runtime network reconfiguration

The system SHALL apply changed output settings - including switching which
backend is active - without requiring a process restart, stopping and
restarting the output thread as needed.

#### Scenario: Applying new settings

- **WHEN** the active backend's settings are changed
- **THEN** subsequent frames are transmitted using the new settings
- **AND** output resumes without restarting the application

#### Scenario: Switching backend takes effect immediately

- **WHEN** the operator switches the active backend
- **THEN** subsequent frames are transmitted through the newly selected
  backend
- **AND** output resumes without restarting the application

### Requirement: Output thread is not blocked by transmission

The system SHALL NOT hold buffer synchronisation while transmitting through
the active backend, so that a slow or unreachable backend cannot delay scene
activation.

#### Scenario: Unreachable node does not stall the interface

- **WHEN** the active backend is unreachable and transmission is slow to fail
- **THEN** scene activation requests continue to be handled without waiting
  for transmission to complete
