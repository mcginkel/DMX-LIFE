## Purpose

Defines how the operator can tell which build of the application they're
running, since releases are tagged and packaged by hand with no automated
build number to fall back on.

## ADDED Requirements

### Requirement: Version visible on every page

The system SHALL display its own version number somewhere visible on every
page of the application.

#### Scenario: Version appears on load

- **WHEN** the operator loads any page of the application
- **THEN** the current version number is visible on that page

#### Scenario: A new release changes the displayed value

- **WHEN** the maintained version value is updated as part of a release and
  the application is restarted
- **THEN** the newly displayed version reflects the updated value

### Requirement: Missing version source does not affect availability

The system SHALL start and render every page normally even if its version
source is missing or unreadable, showing a clear placeholder in place of a
real version number rather than an error or a failed start.

#### Scenario: Version source is missing

- **WHEN** the version source cannot be found or read
- **THEN** the application starts and every page renders normally
- **AND** the version display shows a placeholder such as "unknown"
