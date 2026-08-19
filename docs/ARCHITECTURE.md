# DMX Life - Architecture Overview

This is an orientation map, not a reference manual. For **why** something is
built the way it is, see [`docs/adr/`](adr/) — each decision with its
trade-offs reasoned through. For **what the system does**, in testable terms,
see [`openspec/specs/`](../openspec/specs/). This document exists to help a
reader find their way into the code; it deliberately doesn't duplicate either
of those.

## Module map

```
┌─────────────────────────────────────────────────────────┐
│                     Flask Application                    │
│                   (app/__init__.py)                      │
└──────────────────────┬────────────────────────────────────┘
                        │
                        ├─► Views (Blueprints)
                        │   ├─► main_bp (app/views/main.py)
                        │   └─► setup_bp (app/views/setup.py)
                        │
                        └─► DMX Integration Layer
                            (app/dmx_controller.py)
                            │
                            ├─► ConfigManager (app/config_manager.py)
                            ├─► SceneManager (app/scene_manager.py)
                            └─► DMXController (app/dmx_controller_class.py)
                                └─► StupidArtnet (Art-Net protocol)
```

Why this layering exists: [ADR-0012](adr/0012-app-factory-with-module-singletons.md).

## Components

- **ConfigManager** (`app/config_manager.py`) — all `config.json` I/O.
  `read()` / `write()` (atomic, temp-file + rename — [ADR-0001](adr/0001-json-file-as-system-of-record.md)),
  plus typed accessors (`get_fixtures()`, `get_scenes()`, `save_scene()`,
  `delete_scene()`, `get_network_settings()`...). `read()` also migrates
  legacy positional fixture links to name references on the fly
  ([`fix-fixture-link-references`](../openspec/changes/archive/2026-08-19-fix-fixture-link-references/)).
  No business logic — pure persistence.

- **SceneManager** (`app/scene_manager.py`) — scene composition.
  `toggle_scene(name)` adds or removes a scene from the active layer set and
  rebuilds the full 512-channel frame from every remaining active layer, in
  activation order. `get_active_scenes()` returns that set.
  See [ADR-0005](adr/0005-layered-scene-state.md) (layering),
  [ADR-0006](adr/0006-scene-groups.md) (exclusive vs. additive
  groups), and [ADR-0007](adr/0007-sparse-overlay-via-empty-enabled-fixtures.md)
  (the `enabledFixtures` sparse-overlay distinction).

- **DMXController** (`app/dmx_controller_class.py`) — Art-Net output.
  `set_with_transition(buffer)` starts a 3-second fade; `set_immediate(buffer)`
  applies instantly (scene preview). A background thread transmits
  continuously at ~30fps regardless of whether anything changed. A single
  lock guards `current_values`/`target_values`/the transition flag together,
  so every transmitted frame is one composition, never a mix of two; the
  socket send itself happens outside the lock so an unreachable node can't
  stall a writer. See [ADR-0002](adr/0002-artnet-via-direct-socket-sends.md),
  [ADR-0003](adr/0003-continuous-dmx-output-thread.md),
  [ADR-0004](adr/0004-fixed-linear-crossfade.md), and the
  [`thread-safe-dmx-buffers`](../openspec/changes/archive/2026-08-19-thread-safe-dmx-buffers/)
  change for the locking specifically.

- **Integration layer** (`app/dmx_controller.py`) — wires the three together
  behind a flat function API (`activate_scene()`, `test_scene()`,
  `get_config()`, `save_config()`...) that views import from directly, so
  they never touch the classes.

## Web layer

- `main_bp` (`app/views/main.py`): `/`, `/api/scenes`,
  `POST /api/scenes/activate` (toggles a scene; returns the full active
  list), `/api/dmx/values`, `/api/connection/status`.
- `setup_bp` (`app/views/setup.py`, mounted at `/setup`): network/fixture/scene
  editor pages plus their `/api/config/...` endpoints.

## Frontend

Server-rendered Jinja templates, one vanilla-JS file per page
(`app/static/js/`), no build step, no shared client state
([ADR-0011](adr/0011-server-rendered-vanilla-frontend.md)). On the
main scene page, `main.js` mirrors whatever active-scene list the server
returns rather than tracking state itself — the highlighted buttons are
always a direct reflection of the server's layer set.

## Data flow: activating a scene

```
Click → POST /api/scenes/activate {scene}
      → activate_scene(name)
      → SceneManager.toggle_scene(name)
          - add/remove name from the active layer set (respecting
            exclusive-group membership)
          - rebuild a fresh 512-byte buffer from every remaining layer
      → DMXController.set_with_transition(buffer)
      → response includes every currently active scene name
      → background thread fades current_values toward target_values
        over 3s, transmitting continuously throughout
```

## Configuration

Single JSON file, `app/config.json`, holding network settings, fixtures, and
scenes. Written via temp-file + atomic rename with a `.bak` of the previous
version kept alongside it. See
[`configuration-persistence`](../openspec/specs/configuration-persistence/spec.md).

## Where to look for open work

Known gaps and planned changes are tracked as OpenSpec proposals, not as a
wishlist in this file — see [`openspec/changes/`](../openspec/changes/) for
what's in flight and [`openspec/changes/archive/`](../openspec/changes/archive/)
for what's already landed.

## Testing

No automated test suite yet (tracked as
[`add-test-suite`](../openspec/changes/) if still open — check
`openspec list`). Until then: `./start.sh`, exercise the change through the
UI, use "Test Scene" for immediate DMX feedback, check `config.json` after
saves.

## Troubleshooting

**Server won't start - "Address already in use"**
`lsof -i :5050`, then `./stop.sh` or `kill $(cat dmx_life.pid)`.

**Server refuses to start with a credentials error**
Binding to a non-loopback host requires `DMXLIFE_USERNAME`/`DMXLIFE_PASSWORD`
(see `README.md`). Loopback-only falls back to development defaults.

**No DMX output**
Check the Art-Net IP in Network Setup, confirm fixtures are powered, check
`GET /api/connection/status`, and verify fixture channel ranges don't overlap
(Fixture Setup flags overlaps on save).

**Scenes not saving**
Check `config.json` file permissions and the scene count against the
configured limit (`MAX_SCENES` in `app/__init__.py`); check `nohup.out` for
errors.

**A scene toggle didn't do what I expected**
Remember scenes are layers, not a single active scene — check
`GET /api/dmx/values` for the current `active_scenes` list, and see
[ADR-0005](adr/0005-layered-scene-state.md) for how layering resolves
conflicting channels (last-activated wins).
