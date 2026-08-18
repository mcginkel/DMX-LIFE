# Design: automated test suite

## Context

The obstacle to testing this codebase is not the logic — it is that the logic is
reachable only through objects that open sockets and start threads.
`init_dmx_controller(app)` constructs all three collaborators and the DMX thread
starts from a `before_request` hook
([ADR-0012](../../../docs/adr/0012-app-factory-with-module-singletons.md)).

So the design question is: how much of that do we work around, and how much do
we change?

## Decisions

### Test the classes directly, not through the globals

`SceneManager`, `ConfigManager` and `DMXController` are all independently
constructible. The module-level singletons exist for the convenience of views,
not because the classes require them.

Most tests therefore construct the class under test directly with a fake
collaborator, and never touch `app.dmx_controller`'s globals. This sidesteps the
injection problem entirely rather than refactoring to solve it.

`SceneManager` needs only an object exposing `get_scenes()`, `get_fixtures()`
and `get_scene_by_name()` — a small hand-written fake, no mocking framework.

### The scene-composition tests are the centrepiece

Given a set of fixtures and scenes, `toggle_scene()` returns a 512-byte buffer.
That is a pure function of the active set, so the tests are plain assertions on
byte values. They should cover, at minimum:

- Toggling a scene on, then off, restores the underlying layer's values.
- Toggling off the only claimant of a channel yields 0.
- Activating within an exclusive group replaces the group's member.
- Activating across groups accumulates.
- A sparse overlay writes only its own channels and leaves the rest of an
  overlapping fixture intact.
- Later layers win contested channels.

These mirror the scenarios in `openspec/specs/scene-control/spec.md` one for
one, deliberately.

### `DMXController`: stub the socket, drive the clock

Test the arithmetic, not the thread. Construct the controller, replace
`_send_dmx_packet` with a recorder, never call `start()`, and invoke
`_update_transition()` directly with a controlled `transition_start_time`. This
covers interpolation and the exact-target snap without any timing flakiness.

Testing the thread itself is explicitly out of scope: a test that sleeps is a
test that fails on a loaded CI machine.

### API tests use a temporary config

`create_app()` accepts a config override, so tests can point `CONFIG_FILE` at a
`tmp_path` copy. This keeps the real `app/config.json` out of the test path —
which matters, since exploratory testing against the live config has already
deleted a real scene once.

The DMX controller will still initialise. Stub the Art-Net send at the class
level for the duration of the API tests so nothing reaches the network.

### No fixtures library, no factories

The rig is small enough to declare inline. A shared `conftest.py` provides one
representative fixture set — a couple of multi-channel fixtures with adjacent
addresses, matching the real patch's shape — and tests build scenes on top.

## Risks

- **Tests that encode current bugs as expected behaviour.** Real risk given that
  several endpoints return 500 today. Mitigated by sequencing after
  `fix-request-validation`, and by writing assertions from the specs rather than
  from observed output.
- **The socket stub drifting from the real send path.** Accepted; the alternative
  is asserting on UDP traffic, which is worse.

## Open questions

- Is a GitHub Actions workflow wanted, or is running `pytest` locally enough?
  For a single-maintainer project deployed by copying files, local may be
  sufficient — but CI would at least stop a broken commit reaching the show
  laptop.
