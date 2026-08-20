## ADDED Requirements

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
