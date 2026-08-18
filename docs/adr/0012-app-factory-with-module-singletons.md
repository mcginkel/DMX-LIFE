# ADR-0012: App factory with module-level singletons

- **Status:** Accepted
- **Date:** 2026-08-18 (documented retroactively)

## Context

Three long-lived objects cooperate to run the system: `ConfigManager` (file
I/O), `SceneManager` (scene state and buffer construction), and `DMXController`
(the Art-Net thread). Flask view functions need access to all three.

The DMX controller in particular owns a background thread and a UDP socket.
There must be exactly one of it in the process — a second instance would fight
the first for the wire.

## Decision

Use Flask's application-factory pattern (`create_app()` in `app/__init__.py`)
for the web app, and hold the three collaborators as **module-level globals**
in `app/dmx_controller.py`, wired together once by `init_dmx_controller(app)`.

`app/dmx_controller.py` then acts as a facade: views import free functions
(`activate_scene`, `save_config`, `get_connection_status`, …) rather than
touching the objects. The module docstring calls this the "Integration Layer —
Provides backward-compatible API", because it preserves the function signatures
that existed before the code was split out of a single 433-line module.

## Consequences

**Good:**

- Views stay thin and readable: `from app.dmx_controller import activate_scene`.
- Singleton-ness is structural — there is one module, therefore one controller.
- The facade decouples views from the class layout, which is what allowed
  `build_dmx_buffer()` to be replaced by `toggle_scene()`
  ([ADR-0005](0005-layered-scene-state.md)) while touching only one call site.
- The three classes themselves are independently constructible and therefore
  unit-testable, even though nothing tests them yet.

**Bad:**

- **Globals make isolated testing awkward.** Any test of a view has to go
  through `init_dmx_controller()`, which opens a real socket and starts a real
  thread. There is no injection seam.
- **Initialisation is split across two places** — `create_app()` constructs the
  objects, but the thread starts later from a `@app.before_request` hook. This
  makes lifetime harder to follow, and means no DMX flows until the first HTTP
  request.
- `create_app()` also loads `config.json` wholesale into `app.config`, so
  application settings and domain data (`fixtures`, `scenes`) end up in the
  same namespace as `SECRET_KEY`. Harmless today, confusing to read.
- The "backward-compatible API" framing has outlived its purpose: nothing
  external depends on those signatures, so the indirection is now cost without
  benefit.
- Module-level mutable globals mean import order matters, and a failed
  initialisation leaves `None`s that every function must defensively check —
  which they all do, repetitively.

## Alternatives considered

- **Flask extension pattern** (`app.extensions['dmx']`). Idiomatic, scopes the
  objects to the app instance, and makes multiple apps in one process possible.
  Modest refactor; the natural cleanup if testing becomes a priority.
- **Dependency injection into views.** Most testable, least idiomatic for Flask,
  and verbose for an application this size.
- **Keep everything in one module.** What this replaced. The original 433-line
  file is still present as `app/dmx_controller_old.py` and is now dead code.
