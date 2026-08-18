## ADDED Requirements

### Requirement: Frame composition atomicity

The system SHALL ensure that every transmitted frame corresponds to exactly one
scene composition. A frame SHALL NOT contain a mixture of channel values from a
previous composition and a newly applied one.

#### Scenario: Scene change during an output tick

- **WHEN** a new frame is applied while the output thread is preparing to
  transmit
- **THEN** the transmitted frame contains either entirely the previous values or
  entirely the new ones
- **AND** never a partial mixture of the two

#### Scenario: Values and transition state stay consistent

- **WHEN** a fade is started
- **THEN** the output thread observes the new target values and the active
  transition state together
- **AND** never new values with stale transition state

### Requirement: Output thread is not blocked by transmission

The system SHALL NOT hold buffer synchronisation while transmitting to the
network, so that a slow or unreachable Art-Net node cannot delay scene
activation.

#### Scenario: Unreachable node does not stall the interface

- **WHEN** the Art-Net node is unreachable and transmission is slow to fail
- **THEN** scene activation requests continue to be handled without waiting for
  transmission to complete
