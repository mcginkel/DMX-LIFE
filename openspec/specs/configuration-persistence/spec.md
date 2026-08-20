# Configuration Persistence Specification

## Purpose

Defines how the system stores its configuration durably. All fixtures, scenes
and network settings live in a single JSON file, so the integrity of that file
is the integrity of the entire show configuration.

## Requirements

### Requirement: Atomic configuration writes

The system SHALL write configuration such that a reader observes either the
complete previous version or the complete new version, never a partial or empty
file, even if the process is interrupted mid-write.

#### Scenario: Interruption during a write

- **WHEN** the process is terminated while configuration is being written
- **THEN** the stored configuration file remains complete and parseable
- **AND** it contains either the previous configuration or the new one

#### Scenario: Successful write replaces the previous version

- **WHEN** configuration is written successfully
- **THEN** subsequent reads return the new configuration

### Requirement: Durability before visibility

The system SHALL ensure new configuration content is flushed to storage before
it becomes the visible configuration file.

#### Scenario: Power loss immediately after a write

- **WHEN** power is lost immediately after a write reports success
- **THEN** the configuration file is complete and parseable on restart

### Requirement: Previous version retained

The system SHALL retain the immediately previous configuration alongside the
current one, so a bad write can be reverted without external backups.

#### Scenario: Reverting after an unwanted change

- **WHEN** a configuration write has completed
- **THEN** the version that preceded it remains available on disk

### Requirement: Startup on unreadable configuration

The system SHALL report clearly when the configuration file cannot be parsed,
naming the file and the parse failure, rather than failing with an unhandled
error.

#### Scenario: Corrupt configuration at startup

- **WHEN** the application starts and the configuration file cannot be parsed
- **THEN** it reports which file failed and why
- **AND** indicates that the retained previous version can be restored

### Requirement: Daily configuration snapshot

The system SHALL retain a snapshot of the configuration as it stood before
the first change of each calendar day, distinct from the single most recent
previous version already kept by atomic writes, and SHALL keep every such
daily snapshot rather than discarding earlier ones as new ones are created.

#### Scenario: First change of the day creates a snapshot

- **WHEN** a configuration write occurs and no snapshot exists for the
  current date
- **THEN** the configuration as it stood immediately before this write is
  saved as a dated snapshot

#### Scenario: Later changes the same day do not create another snapshot

- **WHEN** a configuration write occurs and a snapshot for the current date
  already exists
- **THEN** no additional snapshot is created

#### Scenario: A new day's snapshot does not remove previous days'

- **WHEN** the first snapshot of a new calendar day is created
- **THEN** every snapshot from a previous day remains on disk unchanged
- **AND** the new day's snapshot exists alongside them

#### Scenario: Snapshot failure does not block the real write

- **WHEN** creating the daily snapshot fails
- **THEN** the configuration write it was guarding still proceeds
- **AND** the failure is logged

#### Scenario: No restore path is provided

- **WHEN** a daily snapshot exists
- **THEN** the system provides no endpoint, UI, or automatic mechanism that
  reads it back - recovery is a manual file operation outside the
  application
