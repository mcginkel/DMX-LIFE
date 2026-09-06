## Context

The server already holds the authoritative set of active scenes and returns it
with every activation response. `main.js` already applies that returned set to
every button rather than tracking state locally. What is missing is any way for
a client that did not make the request to learn the answer: there is no
periodic refresh on the main page at all.

So this is not a state-management problem. The state model is already right;
it simply has one trigger, and that trigger is the client's own click.

Two facts shape the approach:

1. `GET /api/scenes` already returns `active_scenes`. No server work is needed.
2. `/api/dmx/values`, which the DMX monitor polls once a second, *also* returns
   `active_scenes`. The data has been flowing past unused - nothing consumes it
   for button state.

## Goals / Non-Goals

**Goals:**
- Every open client converges on the server's set within about a second.
- A client that was asleep, backgrounded or briefly disconnected converges when
  it returns, without a reload.
- An operator's own press is never visibly undone by a refresh.

**Non-Goals:**
- Any notion of *who* changed what. There is one operator account; attribution
  would be invented data.
- Locking, or preventing two clients from acting at once. Last write wins,
  which is what the server already does.
- Pushing instead of polling - see below.
- Extending this to the setup pages. Scene editing is a single-operator,
  sit-down activity; the main page is the one used by two people at once.

## Decisions

### Poll, rather than push

A one-second poll of `/api/scenes`, matching the pattern already used by the
connection indicator (5s) and the DMX monitor (1s).

Server-sent events would be the better architecture and would remove the
latency floor. Rejected for now on cost and risk: the application runs on the
Werkzeug development server, where every open SSE connection holds a thread for
as long as the page is open. With two or three clients on a venue LAN a poll is
free, needs no new server code, and cannot exhaust a thread pool during a show.

The threshold for revisiting is concrete: a third kind of client - a phone, a
foot pedal, a second operator's tablet - or a felt need for sub-second
response. Neither is true today.

**Alternative considered:** consuming `active_scenes` from `/api/dmx/values`,
which the monitor already polls, and adding no request at all. Rejected: that
only works while the monitor is open, which is exactly when it is least needed.
The main page must converge whether or not the monitor is showing.

### The refresh writes only the indication

The refresh is a read. It applies the returned set to the buttons and does
nothing else - it never activates, never deactivates, and never touches the
DMX output. This is worth stating because the obvious implementation mistake
is to reuse the activation path for convenience, which would make a refresh
capable of changing the lighting.

### A pending action wins over a refresh in flight

The sharp edge. An operator presses a button; a refresh issued a moment earlier
returns afterwards carrying the *older* set; the button visibly flips back and
then forward again when the activation response lands. During a show that reads
as the system ignoring the press.

The rule: while an activation is in flight, refresh responses do not touch the
indication. The activation response is authoritative when it arrives, and
normal refreshing resumes after it.

**Alternative considered:** sequence numbers or timestamps to discard stale
responses generally. Rejected as more machinery than the problem needs - there
is exactly one kind of conflict here, between a refresh and the client's own
pending action, and suppressing during that window covers it.

### Failure is silent

A failed refresh is logged and otherwise ignored - no alert, no visible error.
The connection indicator already tells the operator when the server is
unreachable, and a modal alert popping up mid-show because one poll timed out
would be worse than the staleness it reports. The next successful refresh
converges, which is what the "falls behind and returns" scenario requires.

Note the contrast with the activation path, which *does* alert on failure. That
is correct: a failed activation means the lights did not change and the operator
must know. A failed refresh means the display is briefly stale.

## Risks / Trade-offs

- **A poll every second, forever, per client.** Small, but it is a request on
  every open page for as long as it is open. → The response is a short JSON
  list, the server is on the venue LAN, and the DMX monitor already polls at
  this rate when open. If it ever matters, that is the signal to move to SSE.
- **Convergence is not instant.** Two operators pressing within the same second
  can both briefly see their own view. The server serialises the actual
  activations, so the output is never ambiguous - only the display lags.
- **A background tab keeps polling.** Browsers throttle timers in background
  tabs, which makes this self-limiting, but it also means a backgrounded page
  may be further behind than a second. It converges when foregrounded, which is
  when it is read.

## Open Questions

- Whether one second is the right interval. It matches the monitor and feels
  responsive, but nothing has measured what an operator actually notices. Easy
  to change; not worth guessing at further before it has been used.
