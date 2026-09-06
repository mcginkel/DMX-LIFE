## 1. Refresh the indication periodically

- [x] 1.1 In `app/static/js/main.js`, poll `/api/scenes` on an interval and
      apply the returned `active_scenes` to every scene button's indication.
- [x] 1.2 Factor the "apply a set of active scene names to the buttons" step so
      the activation response and the refresh use the same code path rather
      than two copies that can drift.
- [x] 1.3 The refresh only writes the indication. It must not activate or
      deactivate anything, and must not touch DMX output.
- [x] 1.4 A failed refresh is logged and otherwise ignored - no alert. The
      activation path keeps its alert, because a failed activation means the
      lights did not change.

## 2. Do not fight the operator

- [x] 2.1 While an activation request is in flight, refresh responses must not
      touch the indication.
- [x] 2.2 The activation response is authoritative when it arrives, and normal
      refreshing resumes afterwards.
- [x] 2.3 Confirm this holds when activations overlap - a second press while
      the first is still in flight must not leave refreshing suppressed
      permanently.

## 3. Verify

- [x] 3.1 Two browsers on the main page: activating a scene in one updates the
      other's buttons within about a second, with no reload.
- [x] 3.2 Deactivating in one clears it in the other.
- [x] 3.3 Exclusive groups propagate correctly - activating a `main` scene in
      one browser shows the previously active `main` scene turning off in the
      other, not both appearing active.
- [x] 3.4 A press is never visibly undone: click repeatedly and confirm no
      button flips back and then forward again.
- [x] 3.5 Refreshing does not change DMX output - with a scene active and no
      one pressing anything, the transmitted values stay constant across many
      refresh cycles.
- [x] 3.6 A client that has been disconnected and reconnected converges without
      a reload.
- [x] 3.7 A failed refresh produces no alert and no visible error, and the next
      successful one converges.
- [x] 3.8 The kill-scene and Extra-group indications propagate like any other -
      they are the same mechanism, but they are the states most likely to be
      misread if they lag.
