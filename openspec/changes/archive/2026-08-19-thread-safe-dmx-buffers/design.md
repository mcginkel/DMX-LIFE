# Design: thread-safe DMX buffer access

## Context

`DMXController` owns two 512-byte buffers and one background thread. The
invariant we want is simple to state:

> Every frame transmitted corresponds to exactly one scene composition, never a
> mixture of two.

The constraint that shapes the design: the output thread must never block for
long. It has a 33 ms budget per tick, and a socket send to an unreachable host
can be slow. Holding a lock across the send would let a network problem stall
every scene activation.

## Decisions

### One lock, not per-buffer locks

A single `threading.Lock` guards both buffers. Two locks would allow a writer to
update `target_values` while a reader held only the `current_values` lock, which
reintroduces the problem while adding deadlock ordering rules. There is no
contention pressure that would justify the complexity.

### Send outside the lock, on a copy

The output thread does:

```python
with self._lock:
    if self.transition_active:
        self._update_transition()
    frame = bytes(self.current_values)   # cheap snapshot
self._send_dmx_packet(frame)             # slow, outside the lock
```

The lock covers interpolation and the snapshot. The socket send — the only
operation that can block for a meaningful time — happens outside it. This keeps
the critical section to a bounded, purely CPU-bound region.

`bytes(bytearray)` copies 512 bytes; at 30 Hz that is 15 KB/s of copying, which
is irrelevant.

### `_send_dmx_packet` takes the frame as an argument

It already does. It must **not** read `self.current_values` itself, or the
snapshot is pointless. This is the one thing a future edit could quietly break,
so it is worth a comment at the call site.

### Writers replace the whole buffer under the lock

`set_with_transition()` and `set_immediate()` take the lock for the duration of
their buffer updates and the transition-flag change together. Updating the
values and the flag under one lock is what makes "a frame is one composition"
hold — a reader can never see new values with a stale flag.

`set_immediate()` currently also sends while holding its own state. It should
snapshot under the lock and send outside, matching the thread.

## Deadlock analysis

There is exactly one lock and no nested acquisition. `_send_dmx_packet` does not
acquire it. `current_app.logger` calls inside the send path are outside the
lock. With a single lock and no nesting, deadlock is not reachable.

## Alternatives considered

- **Double buffering with an atomic swap of a reference.** Python reference
  assignment is atomic under the GIL, so swapping a whole `bytes` object would
  give the same guarantee without a lock. Genuinely simpler in some ways, but it
  changes `current_values` from a mutable buffer that external code reads
  (`get_current_values()`, and the monitoring path) into a replaced object, which
  is a wider change than adding a lock.
- **Queue-based hand-off**, where request threads post frames and only the output
  thread touches buffers. Architecturally cleanest and removes shared mutable
  state entirely. Rejected as too large for the defect being fixed; worth
  revisiting if the threading model is ever reworked.
- **Do nothing.** Defensible today — the artefact is one frame inside a 3-second
  fade. Rejected because the safety margin is accidental rather than designed.
