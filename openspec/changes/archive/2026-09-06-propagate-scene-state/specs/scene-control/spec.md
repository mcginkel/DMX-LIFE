## MODIFIED Requirements

### Requirement: Server-authoritative active state

The system SHALL hold the set of active scenes on the server and return it with
every activation response. The interface SHALL derive its indication of what is
active from that set rather than tracking it independently, and SHALL keep that
indication current while a page remains open, so that every connected client
converges on the server's set rather than only the client that caused a change.

#### Scenario: Reload reflects true state

- **WHEN** scenes are active
- **AND** the operator reloads the main page
- **THEN** exactly those scenes are shown as active

#### Scenario: Highlighting follows the server

- **WHEN** an activation response is received
- **THEN** every scene button's active indication is set from the returned list

#### Scenario: A change made elsewhere reaches an open page

- **WHEN** a scene is activated or deactivated from one client
- **AND** another client has the main page open
- **THEN** that other client's indication updates to match the server's active
  set without the operator reloading the page

#### Scenario: A client's own action is not undone by a refresh in flight

- **WHEN** an operator activates a scene
- **AND** a periodic refresh that was issued before that activation returns
  afterwards
- **THEN** the returned older set does not overwrite the indication of the
  action the operator just took

#### Scenario: A page that has fallen behind converges

- **WHEN** a client's connection to the server is interrupted and later
  restored
- **THEN** its indication returns to matching the server's active set without
  the operator reloading the page

#### Scenario: Refreshing does not disturb the output

- **WHEN** the indication is refreshed from the server
- **THEN** no scene is activated or deactivated as a result
- **AND** the transmitted frame is unchanged
