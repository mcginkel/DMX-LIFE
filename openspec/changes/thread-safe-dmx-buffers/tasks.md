# Tasks: make DMX buffer access thread-safe

## 1. Introduce the lock

- [x] 1.1 Add `self._lock = threading.Lock()` to `DMXController.__init__`.
- [x] 1.2 Document the invariant in a comment: every transmitted frame is one
      composition; the lock covers buffer access, never the socket send.

## 2. Output thread

- [x] 2.1 In `_run()`, acquire the lock around the transition update and take a
      `bytes()` snapshot of `current_values` inside it.
- [x] 2.2 Call `_send_dmx_packet(frame)` with the snapshot, outside the lock.
- [x] 2.3 Confirm `_send_dmx_packet` reads only its argument and never
      `self.current_values`. Confirmed by inspection — no change needed, it
      only touches `buffer`, `self.artnet`, and `self.connection_status`.

## 3. Writers

- [x] 3.1 Guard `set_with_transition()` so the target update and the
      transition-flag change happen under one lock acquisition.
- [x] 3.2 Guard `set_immediate()` so both buffers and the flag update together;
      snapshot under the lock and send outside it.
- [x] 3.3 Guard `get_current_values()` so monitoring reads a consistent snapshot.
      Changed its return type from a live `bytearray` reference to an
      immutable `bytes` snapshot — returning the mutable buffer itself,
      even from inside the lock, would let the caller keep reading a
      reference the output thread mutates the instant the lock releases.

      **Scope note:** this method was previously unused — the real read
      path was `app/dmx_controller.py`'s `get_current_dmx_values()`, which
      reached `dmx_controller.current_values` directly, bypassing the class
      entirely. Guarding only `get_current_values()` would have protected
      dead code while leaving the DMX monitor endpoint reading the live,
      unguarded buffer through the actual path it uses. Rerouted
      `get_current_dmx_values()` through `dmx_controller.get_current_values()`
      instead, and removed the now-dead `current_dmx_values = dmx_controller.current_values`
      aliasing assignment in `init_dmx_controller()` that this made stale.
      This touches `app/dmx_controller.py`, which the proposal's "Affected
      code" list didn't name - flagging rather than absorbing silently,
      since without it this whole task would have no observable effect.

## 4. Verify

- [x] 4.1 No nested lock acquisition anywhere in the class (single lock, no
      re-entrancy needed). Confirmed by inspection: `_update_transition` is
      only ever called from inside `_run`'s own `with self._lock` block and
      never acquires it itself; `_send_dmx_packet` never touches the lock.
      Also stress-tested directly: 4 writer threads + 4 reader threads
      hammering one `DMXController` (200 writes/thread alternating
      `set_with_transition`/`set_immediate`, 500 reads/thread), no errors,
      every snapshot came back as valid 512-byte `bytes`.
- [x] 4.2 Fades still run smoothly over their full duration. Sampled channel 1
      over a real 3s fade against the running app - climbed gradually,
      settled exactly at the target value (255).
- [x] 4.3 Scene preview still applies immediately. Verified value landed
      within 0.1s, no gradual movement.
- [x] 4.4 Rapidly toggling scenes produces no visible glitch and no exception.
      30 toggles across 3 scenes against the live server, all HTTP 200, no
      errors in the log, server still responsive after.
- [x] 4.5 With the Art-Net node unreachable, the interface stays responsive and
      scene toggles still return promptly. The configured IP
      (192.168.3.170) is unreachable from the dev machine, so this was
      naturally exercised - `connection_status.last_error_time` confirms
      sends genuinely were failing, yet 20 activation requests completed in
      0.236s total (avg 12ms/request).
- [x] 4.6 The DMX monitor still reports values. Activated a scene, waited for
      the fade to complete, confirmed `/api/dmx/values` returned the exact
      settled target values.

## 5. Follow-up

- [x] 5.1 Consider whether `reconfigure()` needs the same treatment — it stops
      and restarts the thread while replacing the Art-Net object.

      Conclusion: no change needed to the buffer locking. `reconfigure()`
      never touches `current_values`/`target_values` itself - it only
      replaces `self.artnet` - and buffer access during and after
      reconfiguration still goes through the same lock-protected methods
      regardless of which `StupidArtnet` instance is live. `stop()` joins
      the output thread (2s timeout) before `reconfigure()` reassigns
      `self.artnet`, so in the normal case the old thread has fully exited
      before the reassignment happens.

      There is one latent, pre-existing race this change doesn't touch: if
      `join(timeout=2.0)` times out, the old thread could still be mid-call
      to `_send_dmx_packet` with a stale `self.artnet` reference while the
      main thread reassigns it. This is about the Art-Net socket object's
      lifecycle, not DMX frame composition - a different concern from what
      this change's lock protects, and out of scope per the proposal's
      stated impact (`app/dmx_controller_class.py`'s buffer access) and
      non-goals ("reworking the threading model"). Worth its own change if
      it ever proves to matter in practice; not folded in here.
