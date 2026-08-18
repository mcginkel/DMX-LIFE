## ADDED Requirements

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
