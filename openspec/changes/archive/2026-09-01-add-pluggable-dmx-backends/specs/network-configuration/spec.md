## MODIFIED Requirements

### Requirement: Art-Net settings

The system SHALL allow an operator to configure the Art-Net destination address,
port, universe and refresh rate when Art-Net is the active output backend, and
SHALL persist them.

#### Scenario: Saving settings

- **WHEN** the operator submits Art-Net settings while Art-Net is the active
  backend
- **THEN** the settings are persisted
- **AND** subsequent output uses them

#### Scenario: Settings persist across restarts

- **WHEN** the application is restarted
- **THEN** the previously configured Art-Net settings are in effect

#### Scenario: Destination address is required

- **WHEN** a save is attempted without a destination address
- **THEN** the request is rejected and the operator is told the address is
  required

### Requirement: Setting value validation

The system SHALL validate Art-Net setting values before applying them, rejecting
non-numeric or out-of-range values with a client error rather than raising an
unhandled error.

#### Scenario: Non-numeric port

- **WHEN** a request supplies a port that is not a number
- **THEN** the system responds with a client error naming the offending setting
- **AND** the stored configuration is unchanged

#### Scenario: Non-numeric universe or refresh rate

- **WHEN** a request supplies a non-numeric universe or refresh rate
- **THEN** the system responds with a client error
- **AND** the stored configuration is unchanged

#### Scenario: Valid settings are applied

- **WHEN** a request supplies numeric values for port, universe and refresh rate
- **THEN** the settings are stored and applied

### Requirement: Settings applied without restart

The system SHALL apply changed output settings to the running output
immediately, without requiring the operator to restart the application. This
includes both settings for the currently active backend and a change of which
backend is active.

#### Scenario: Changing the destination mid-session

- **WHEN** the operator changes the Art-Net address while Art-Net is the
  active backend and the application is running
- **THEN** output is redirected to the new address
- **AND** no restart is required

## ADDED Requirements

### Requirement: Output backend selection

The system SHALL allow the operator to choose which output backend is active,
as a setting distinct from that backend's own connection settings, and SHALL
persist the selection.

#### Scenario: Choosing a backend

- **WHEN** the operator selects an output backend in Network Setup
- **THEN** the selection is persisted
- **AND** that backend is used for subsequent output

#### Scenario: Backend selection persists across restarts

- **WHEN** the application is restarted
- **THEN** the previously selected backend is active

### Requirement: Per-backend settings

The system SHALL allow each supported backend to define and validate its own
settings independently, so that a setting meaningful to one backend (for
example, a serial device path) does not need to fit the validation rules of
another (for example, a numeric Art-Net port).

#### Scenario: Backend-specific validation

- **WHEN** the operator submits settings for the active backend
- **THEN** those settings are validated according to that backend's own
  requirements, not another backend's
