## Purpose

Defines the contract an output backend must satisfy and how the active one is
selected, so the rest of the system (scene composition, crossfade timing,
frame atomicity) behaves identically no matter which physical transport is
driving the fixtures.

## ADDED Requirements

### Requirement: Backend selection from configuration

The system SHALL determine which output backend is active from
configuration, without requiring a code change to select among already-
implemented backend types.

#### Scenario: Choosing a backend at setup

- **WHEN** the operator selects an output backend and its settings in Network
  Setup
- **THEN** that backend is used for all subsequent output

#### Scenario: Configured backend is not recognised

- **WHEN** the configured backend selection does not match any implemented
  backend
- **THEN** the system reports the problem clearly rather than silently
  falling back to a different backend or crashing

### Requirement: Uniform backend contract

The system SHALL require every backend to provide connecting, transmitting a
complete frame, disconnecting, and reporting its own connection status, so
that the output thread can treat any backend identically.

#### Scenario: Backend failure surfaces through the same channel

- **WHEN** a backend fails to connect or fails to transmit
- **THEN** that failure is reported through the same connection-status
  mechanism regardless of which backend is active

### Requirement: One active backend per installation

The system SHALL support exactly one active output backend at a time. It
SHALL NOT transmit the same frame through multiple backends simultaneously.

#### Scenario: Only the selected backend transmits

- **WHEN** a backend is configured as active
- **THEN** frames are sent only through that backend

### Requirement: Backend independence of output behaviour

The system SHALL NOT vary scene composition, crossfade timing, frame
atomicity, or preview behaviour by which backend is active.

#### Scenario: Crossfade behaves identically across backends

- **WHEN** the same scene is activated once with one backend active and once
  with a different backend active
- **THEN** the crossfade duration and interpolation behave identically in
  both cases - only the physical transport of the output differs
