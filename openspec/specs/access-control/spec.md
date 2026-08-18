# Access Control Specification

## Purpose

Defines who may operate the lighting. The application binds to all interfaces
and is therefore reachable from every device on the venue network; access
control exists to stop a passer-by from altering the lighting during an event.

## Requirements

### Requirement: Authentication on every route

The system SHALL require authentication for every page and every API endpoint,
including scene activation, configuration reads and writes, and monitoring
endpoints.

#### Scenario: Unauthenticated request is refused

- **WHEN** a request is made without valid credentials
- **THEN** the system responds with an authentication challenge
- **AND** does not disclose configuration or change lighting state

#### Scenario: Authenticated request proceeds

- **WHEN** a request is made with valid credentials
- **THEN** the request is handled normally

#### Scenario: Monitoring endpoints are also protected

- **WHEN** an unauthenticated request is made to a monitoring endpoint
- **THEN** it is refused in the same way as any other endpoint

### Requirement: Single operator account

The system SHALL authenticate against a single operator account. It does not
support multiple users, roles, or per-user permissions.

#### Scenario: Correct credentials are accepted

- **WHEN** the configured username and password are supplied
- **THEN** access is granted

#### Scenario: Incorrect credentials are rejected

- **WHEN** an incorrect username or password is supplied
- **THEN** access is denied

### Requirement: Credential storage

The system SHALL obtain the operator credentials from the environment at
application startup and use them for the lifetime of the process. Credentials
SHALL NOT be stored in source code.

#### Scenario: Credentials are fixed for the session

- **WHEN** the application is running
- **THEN** the credentials required for access do not change until it is
  restarted

#### Scenario: Deployment supplies its own credentials

- **WHEN** credentials are supplied through environment variables
- **THEN** those credentials are required for access

#### Scenario: Network binding without configured credentials

- **WHEN** the application is started bound to a non-loopback interface
- **AND** no credentials are supplied through the environment
- **THEN** the application refuses to start and explains which variables are
  required

#### Scenario: Local development without configured credentials

- **WHEN** the application is started bound to loopback only
- **AND** no credentials are supplied through the environment
- **THEN** the application starts with development defaults
- **AND** warns that development credentials are in use

### Requirement: Constant-time credential comparison

The system SHALL compare supplied credentials against the configured ones using
a constant-time comparison.

#### Scenario: Comparison does not leak timing information

- **WHEN** credentials are verified
- **THEN** the comparison takes the same time regardless of how many leading
  characters match

### Requirement: Debugger disabled by default

The system SHALL disable the interactive debugger by default and SHALL enable it
only when explicitly requested through the environment.

#### Scenario: Default start has no debugger

- **WHEN** the application is started without explicitly enabling debug mode
- **THEN** the interactive debugger is not served on unhandled exceptions

#### Scenario: Debugger is refused on a network interface

- **WHEN** debug mode is explicitly enabled
- **AND** the application is bound to a non-loopback interface
- **THEN** the application refuses to start and explains the risk

#### Scenario: Debugger permitted on loopback

- **WHEN** debug mode is explicitly enabled
- **AND** the application is bound to loopback only
- **THEN** the application starts with the debugger enabled
