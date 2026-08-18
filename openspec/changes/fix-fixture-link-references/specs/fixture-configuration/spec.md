## MODIFIED Requirements

### Requirement: Fixture linking

The system SHALL allow a fixture to be linked to another fixture of the same
type, designating that other fixture as its master, so that edits to the master
propagate to its linked fixtures. The link SHALL identify the master by name, so
that it remains correct when fixtures are added, removed or reordered.

#### Scenario: Linked fixtures follow the master while editing

- **WHEN** the operator adjusts a channel on a master fixture in the scene
  editor
- **THEN** the corresponding channel on each fixture linked to it receives the
  same value

#### Scenario: Linking is restricted to matching types

- **WHEN** the operator attempts to link a fixture to one of a different type
- **THEN** the link is rejected

#### Scenario: Chains and self-links are prevented

- **WHEN** the operator attempts to link a fixture to itself, or to a fixture
  that already has fixtures linked to it
- **THEN** the link is rejected

#### Scenario: Links survive reordering

- **WHEN** fixtures are added, removed or reordered
- **THEN** existing links continue to reference the same master fixtures

### Requirement: Link maintenance on deletion

When a fixture is deleted, the system SHALL clear links that referenced it, so
that no link points at a fixture that no longer exists.

#### Scenario: Links to a deleted fixture are cleared

- **WHEN** a fixture that other fixtures were linked to is deleted
- **THEN** those fixtures are left unlinked

#### Scenario: References are corrected after removal

- **WHEN** a fixture earlier in the list is deleted
- **THEN** links between the remaining fixtures continue to reference the same
  masters
- **AND** no positional adjustment is required to achieve this

## ADDED Requirements

### Requirement: Server-side link validation

The system SHALL validate fixture links when they are saved, rejecting a link
whose master does not exist, is the fixture itself, is of a different type, or is
itself linked to another fixture.

#### Scenario: Link to a non-existent fixture

- **WHEN** a save request links a fixture to a master that does not exist
- **THEN** the request is rejected with a client error

#### Scenario: Self-link submitted directly to the API

- **WHEN** a save request links a fixture to itself
- **THEN** the request is rejected with a client error

#### Scenario: Link forming a chain

- **WHEN** a save request links a fixture to a master that is itself linked
- **THEN** the request is rejected with a client error

### Requirement: Unique fixture names

The system SHALL require fixture names to be unique, so that a name
unambiguously identifies one fixture.

#### Scenario: Duplicate name rejected

- **WHEN** a save request would result in two fixtures sharing a name
- **THEN** the request is rejected with a client error

### Requirement: Migration of positional link references

The system SHALL accept configurations in which links are stored as positional
indices, converting them to name references on load, and SHALL report any link
it cannot resolve rather than silently discarding it.

#### Scenario: Valid positional reference is converted

- **WHEN** a stored link is an index pointing at a different fixture of the same
  type
- **THEN** it is converted to that fixture's name

#### Scenario: Unresolvable reference is reported

- **WHEN** a stored link cannot be resolved to a valid master
- **THEN** the fixture is left unlinked
- **AND** the system reports which fixture was affected
