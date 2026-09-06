## ADDED Requirements

### Requirement: Operator data separate from the software distribution

The system SHALL store the configuration it reads and writes at runtime
outside the software distribution, so that replacing, updating or reinstalling
the software neither reads operator data from the distribution nor writes
operator data into it.

#### Scenario: Updating the software preserves operator data

- **WHEN** the software is updated or replaced in place
- **THEN** the fixtures, scenes and output settings in use before the update
  are still in effect afterwards

#### Scenario: Operator edits do not obstruct a software update

- **WHEN** an operator has saved changes since the software was installed
- **AND** the software is updated or replaced
- **THEN** the update proceeds without requiring those changes to be discarded

#### Scenario: Operator data is not carried by the distribution

- **WHEN** the software distribution is inspected after an operator has made
  changes
- **THEN** it contains no record of those changes

### Requirement: First run seeds operator data from a shipped default

The system SHALL ship a default configuration and, when no operator
configuration exists at the operator data location, SHALL create one from that
default before serving any request. It SHALL NOT write to the shipped default
at any point.

#### Scenario: A fresh installation starts usable

- **WHEN** the application starts and no operator configuration exists
- **THEN** one is created from the shipped default
- **AND** the application starts normally with that configuration in effect

#### Scenario: An existing installation is left alone

- **WHEN** the application starts and operator configuration already exists
- **THEN** it is used as-is
- **AND** the shipped default is not consulted or applied

#### Scenario: The shipped default is never modified

- **WHEN** an operator saves any configuration change
- **THEN** the shipped default is unchanged

### Requirement: Operator data location is configurable

The system SHALL resolve the operator data location from the environment,
falling back to a documented default when the environment does not specify
one, so that a deployment can place operator data where its own backup and
synchronisation arrangements expect it.

#### Scenario: Location supplied by the environment

- **WHEN** the operator data location is set in the environment
- **THEN** configuration is read from and written to that location

#### Scenario: No location supplied

- **WHEN** the operator data location is not set in the environment
- **THEN** the documented default location is used

#### Scenario: Location is reported at startup

- **WHEN** the application starts
- **THEN** it reports which operator data location is in effect, so that an
  operator can tell which data the running instance is using

### Requirement: Derived configuration files accompany the operator data

The system SHALL place every file it derives from the configuration - the
retained previous version and the dated daily snapshots - alongside the
operator configuration rather than in the software distribution, so that
operator data is contained in one location.

#### Scenario: Retained previous version sits with the operator data

- **WHEN** a configuration write completes
- **THEN** the retained previous version is stored alongside the operator
  configuration

#### Scenario: Daily snapshots sit with the operator data

- **WHEN** a daily snapshot is created
- **THEN** it is stored alongside the operator configuration

#### Scenario: Copying the operator data location captures everything

- **WHEN** the operator data location is copied elsewhere
- **THEN** the copy contains the configuration, its retained previous version
  and every daily snapshot, with no operator data left behind
