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

The system SHALL obtain the operator credentials at application startup and use
them for the lifetime of the process.

#### Scenario: Credentials are fixed for the session

- **WHEN** the application is running
- **THEN** the credentials required for access do not change until it is
  restarted

> **As-built note:** credentials are currently hardcoded constants in
> `app/__init__.py` and cannot be changed without editing source. This is a
> known weakness, not a design goal — see
> [ADR-0013](../../../docs/adr/0013-http-basic-auth.md). The
> `secure-auth-and-debug` change proposes making them configurable.
