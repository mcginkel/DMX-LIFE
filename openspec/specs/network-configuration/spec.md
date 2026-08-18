# Network Configuration Specification

## Purpose

Defines how the operator points the system at the Art-Net node that drives the
rig — the destination address, universe, and output rate — and how those
settings take effect.

## Requirements

### Requirement: Art-Net settings

The system SHALL allow an operator to configure the Art-Net destination address,
port, universe and refresh rate, and SHALL persist them.

#### Scenario: Saving settings

- **WHEN** the operator submits Art-Net settings
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

### Requirement: Broadcast output

The system SHALL support directing output either to a specific node address or
to the network broadcast address, so that a rig can be driven without knowing
the node's address.

#### Scenario: Broadcasting to the local network

- **WHEN** the destination address is set to the broadcast address
- **THEN** frames are broadcast rather than sent to a single host

### Requirement: Settings applied without restart

The system SHALL apply changed Art-Net settings to the running output
immediately, without requiring the operator to restart the application.

#### Scenario: Changing the destination mid-session

- **WHEN** the operator changes the Art-Net address while the application is
  running
- **THEN** output is redirected to the new address
- **AND** no restart is required

### Requirement: Defaults for first run

The system SHALL create a usable default configuration when no configuration
file exists, so that a fresh installation starts successfully.

#### Scenario: First start with no configuration

- **WHEN** the application starts and no configuration file is present
- **THEN** a default configuration is created with broadcast output and an empty
  fixture and scene list
- **AND** the application starts normally
