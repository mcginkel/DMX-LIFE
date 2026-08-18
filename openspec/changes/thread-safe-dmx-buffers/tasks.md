# Tasks: make DMX buffer access thread-safe

## 1. Introduce the lock

- [ ] 1.1 Add `self._lock = threading.Lock()` to `DMXController.__init__`.
- [ ] 1.2 Document the invariant in a comment: every transmitted frame is one
      composition; the lock covers buffer access, never the socket send.

## 2. Output thread

- [ ] 2.1 In `_run()`, acquire the lock around the transition update and take a
      `bytes()` snapshot of `current_values` inside it.
- [ ] 2.2 Call `_send_dmx_packet(frame)` with the snapshot, outside the lock.
- [ ] 2.3 Confirm `_send_dmx_packet` reads only its argument and never
      `self.current_values`.

## 3. Writers

- [ ] 3.1 Guard `set_with_transition()` so the target update and the
      transition-flag change happen under one lock acquisition.
- [ ] 3.2 Guard `set_immediate()` so both buffers and the flag update together;
      snapshot under the lock and send outside it.
- [ ] 3.3 Guard `get_current_values()` so monitoring reads a consistent snapshot.

## 4. Verify

- [ ] 4.1 No nested lock acquisition anywhere in the class (single lock, no
      re-entrancy needed).
- [ ] 4.2 Fades still run smoothly over their full duration.
- [ ] 4.3 Scene preview still applies immediately.
- [ ] 4.4 Rapidly toggling scenes produces no visible glitch and no exception.
- [ ] 4.5 With the Art-Net node unreachable, the interface stays responsive and
      scene toggles still return promptly.
- [ ] 4.6 The DMX monitor still reports values.

## 5. Follow-up

- [ ] 5.1 Consider whether `reconfigure()` needs the same treatment — it stops
      and restarts the thread while replacing the Art-Net object.
