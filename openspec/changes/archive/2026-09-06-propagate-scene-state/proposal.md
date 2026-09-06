## Why

Two browsers can control the system at once - a laptop at the desk and a tablet
in the room is the obvious pairing - but only the browser that pressed the
button knows what happened. The other keeps showing whatever was active when it
last loaded.

The server already holds the authoritative set of active scenes and returns it
with every activation response. `scene-control` requires exactly that, and
requires the interface to derive its indication from the returned set rather
than tracking state itself. What is missing is any way for a client that did
not make the request to learn the answer. `main.js` has no polling at all.

The data is already flowing past unused: `/api/dmx/values`, which the DMX
monitor polls every second, returns `active_scenes` in its response. Nothing
consumes it for button state.

During a show this matters more than it sounds. Two operators, or one operator
who has walked to the other end of the room, see different pictures of what is
live, and pressing a button on the stale one is a toggle in the wrong
direction.

## What Changes

- Every connected client's scene buttons reflect the server's active set within
  about a second, regardless of which client caused the change.
- The main page acquires the periodic refresh it currently lacks, matching the
  pattern already used for connection status and the DMX monitor.
- A client that has been disconnected or asleep converges on the correct state
  when it returns, rather than staying stale until reloaded.
- Deliberately polling rather than pushing, at least to begin with: for a
  handful of clients on a venue LAN the cost is negligible, it matches the
  existing pattern, and it needs no long-lived connections on the development
  server the application runs on. A push mechanism is the better architecture
  and worth revisiting if a phone, a pedal, or a third operator ever joins.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `scene-control`: "Server-authoritative active state" requires the interface
  to derive its indication from the server's returned set, but only in response
  to that client's own activation. It gains a requirement that the indication
  converges for every connected client, not only the one that acted.

## Impact

- Affected code: `app/static/js/main.js` (the periodic refresh and applying the
  returned set to button state). No server change is expected - `/api/scenes`
  already returns what is needed.
- Load: one small request per client per interval. With the DMX monitor open a
  client already polls once a second, so this is not a new order of magnitude.
- Interaction risk to design around: a refresh landing between an operator's
  press and the server's response could visibly flip a button back and then
  forward again. The specification should require that a client's own pending
  action is not overwritten by a refresh in flight.
- Not included: any notion of which client did what, or of locking a scene
  while another operator is editing it.
