# ADR-0003: Continuous DMX output from a dedicated thread

- **Status:** Accepted
- **Date:** 2026-08-18 (documented retroactively)

## Context

DMX lighting nodes expect a continuous stream of frames. Many implementations
treat a gap in the stream as a fault and either hold the last value or fade to
black, depending on the fixture. Sending only when a scene changes is therefore
risky, and it also makes it impossible to notice that the network has gone away
between scene changes.

Separately, crossfades (see [ADR-0004](0004-fixed-linear-crossfade.md)) require
the DMX values to be recomputed many times per second, independently of HTTP
request handling.

## Decision

`DMXController.start()` spawns one daemon thread that runs for the lifetime of
the process. Its loop, at roughly 30 Hz (`UPDATE_RATE = 0.033`):

1. Sleep 33 ms.
2. If a transition is active, advance the interpolation.
3. Send the current 512-byte buffer, **always** — whether or not anything
   changed.

The thread is started lazily from a Flask `@app.before_request` hook the first
time a request arrives, guarded by an `app._dmx_initialized` flag.

## Consequences

**Good:**

- Fixtures receive a continuous stream, which is what the protocol and the
  hardware expect.
- Connection state is continuously verified: because a packet is sent every
  33 ms, a dropped link is detected within one frame rather than at the next
  scene change.
- Fades are smooth and independent of web traffic — no HTTP request is needed
  to drive an in-progress transition to completion.

**Bad:**

- **The output buffers are shared mutable state with no lock.** The DMX thread
  reads and writes `current_values` while request threads write `target_values`
  and `current_values` (via `set_immediate`). In CPython the GIL makes
  individual `bytearray` element assignments atomic, so this does not corrupt
  memory, but a scene change landing mid-interpolation can produce a frame that
  mixes values from two scenes. In practice this is invisible during a 3-second
  fade; it is still an unsound design.
- Constant CPU and network use even when idle: ~30 packets/second, forever.
- Lazy start via `before_request` means the DMX stream does not begin until the
  first HTTP request. A freshly started server outputs nothing until someone
  opens the page.
- The daemon thread is never joined on shutdown; the process simply exits.

## Alternatives considered

- **Send only on change.** Lower overhead, but loses connection monitoring and
  risks fixtures interpreting the silence as a fault.
- **Start the thread at app-factory time instead of on first request.** Cleaner,
  and removes the "silent until first request" gap. Not done originally because
  Flask's reloader runs the factory twice in debug mode, which would produce two
  competing DMX threads. Worth revisiting alongside
  [ADR-0013](0013-http-basic-auth.md)'s debug-mode cleanup.
- **`asyncio` instead of a thread.** No real benefit for one periodic task, and
  it would force the whole Flask app into an async stack.
