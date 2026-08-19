# Make DMX buffer access thread-safe

## Why

Two threads share the DMX buffers with no synchronisation:

- The **output thread** ([ADR-0003](../../../docs/adr/0003-continuous-dmx-output-thread.md))
  reads and writes `current_values` roughly every 33 ms while interpolating, and
  reads it again to build each outgoing packet.
- **Request threads** write `target_values` in `set_with_transition()`, and write
  both buffers in `set_immediate()`, whenever the operator clicks a scene.

CPython's GIL makes each individual `bytearray` element assignment atomic, so
this cannot corrupt memory or crash. The real defect is subtler: neither the
512-element update loops nor the packet build are atomic as a whole, so the
output thread can observe a buffer that is **half-written**.

Concretely, a scene activation that lands between two ticks of the output thread
can produce one transmitted frame where some channels carry the new scene's
values and the rest carry the old — a single frame of a look that was never
intended. At 30 fps during a 3-second fade this is invisible in practice, which
is exactly why it has never been reported.

It matters now because the failure mode gets worse as the system grows. A
shorter fade, a snap cue, or any future feature that writes buffers from a
second place turns a one-frame artefact into a visible glitch. The current
correctness rests on "the fade is long enough to hide it", which is not a
property anyone chose.

## What changes

- Add a `threading.Lock` to `DMXController`, guarding all buffer access.
- Hold it around the interpolation step, the packet build, and both public
  setters, so that every transmitted frame corresponds to exactly one
  composition.
- Keep the critical sections short: copy the buffer under the lock, then send
  outside it, so a slow or blocking socket send never stalls a request thread.

## Non-goals

- Changing the fade behaviour, duration, or curve
  ([ADR-0004](../../../docs/adr/0004-fixed-linear-crossfade.md)).
- Reworking the threading model. One output thread remains correct; this change
  makes the existing model sound rather than replacing it.
- Optimising the interpolation loop.

## Impact

- Affected specs: `dmx-output`
- Affected code: `app/dmx_controller_class.py`
- **Performance:** the lock is uncontended in the common case — one writer at
  human click rates against a 30 Hz reader. Expected cost is negligible.
- **Risk:** the main hazard of this change is introducing a deadlock or holding
  the lock across the socket send and stalling the output thread. The design
  addresses both explicitly.
