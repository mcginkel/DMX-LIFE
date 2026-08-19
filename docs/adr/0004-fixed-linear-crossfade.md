# ADR-0004: Fixed-duration linear crossfade

- **Status:** Accepted
- **Date:** 2026-08-18 (documented retroactively)

## Context

Snapping instantly from one lighting state to another looks abrupt and
amateurish in a live room. Scene changes need to fade. The original design
brief (formerly `design/prompt.txt`, later removed from the working tree —
see git history) called for a 2-second transition.

The operator also needs a way to preview a scene while editing it, where a fade
would just get in the way of judging the result.

## Decision

Every scene activation fades over a fixed **3 seconds** using linear
interpolation, applied per channel by the DMX output thread:

```python
progress = min(elapsed / TRANSITION_DURATION, 1.0)
interpolated = int(current + (target - current) * progress)
```

`TRANSITION_DURATION = 3.0` is a class constant on `DMXController`. It is not
configurable through the UI or `config.json`.

Scene *testing* from the editor bypasses this entirely via `set_immediate()`,
which writes both buffers and sends at once.

## Consequences

**Good:**

- Scene changes look deliberate and calm. 3 seconds was chosen over the
  specified 2 after watching both; 2 still read as slightly hurried.
- One code path, no per-scene configuration to get wrong mid-show.
- Preview stays instant, so editing a scene gives immediate feedback.

**Bad:**

- **Not configurable.** A fast blackout or a snap cue is impossible without
  editing Python. This is the most likely constraint to become annoying.
- **Interpolation is recomputed from the live value each frame**, not from a
  captured start value. Because `current` is re-read every tick and `progress`
  grows linearly, the actual curve is slightly ease-out rather than truly
  linear, and integer truncation can leave a channel one step short until the
  final snap-to-target at `progress >= 1.0`.
- Starting a new transition mid-fade restarts the clock from wherever the
  channels currently sit. Usually the desired behaviour, but it means the total
  time to reach the final state can exceed 3 seconds.
- The undocumented deviation from the 2-second brief has confused readers of
  the original spec; that is part of why this ADR exists.

## Alternatives considered

- **Per-scene fade times.** The obvious next step and probably the right one
  eventually. Deferred to keep the scene schema and the editor UI simple.
- **Non-linear easing (S-curve).** Perceptually smoother for dimming, since
  human brightness perception is non-linear. Rejected for now as a refinement
  that does not change what the tool can do.
- **Fade on a per-channel basis with different rates.** Real consoles do this.
  Far beyond the needs of this tool.
