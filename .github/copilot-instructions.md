# DMX Life - Copilot Instructions

## Project Overview
DMX Life is a Flask web application for controlling DMX lighting fixtures via Art-Net protocol. Users create lighting scenes with selective fixture control and activate them through a simple web interface.

**Design Philosophy**: Built for non-technical users with focus on simplicity and intuitive controls. See `docs/adr/` for why decisions were made, and `openspec/specs/` for what the system does today, in testable terms. (The original design brief lived at `design/prompt.txt`; it was later removed from the working tree - still recoverable via `git log --all --full-history -- design/prompt.txt` if needed.)

## Architecture

### Modular Backend Structure (Refactored December 2024)

The application follows a **modular architecture** with clear separation of concerns:

#### Core Components

1. **ConfigManager** (`app/config_manager.py`)
   - Handles all JSON configuration file I/O
   - Methods: `read()`, `write()`, `update()`, `save_scene()`, `delete_scene()`, etc.
   - No business logic - pure data persistence layer
   - Auto-creates default config if missing

2. **SceneManager** (`app/scene_manager.py`)
   - Tracks the set of currently active scene layers and composes the DMX
     frame from all of them (see "Scene Activation with Selective Fixtures"
     below - this is not a single-active-scene model)
   - Methods: `load_scenes()`, `toggle_scene(name)`, `get_active_scenes()`, etc.
   - Caches scenes for performance

3. **DMXController** (`app/dmx_controller_class.py`)
   - Controls StupidArtnet hardware interface
   - Manages background thread for continuous DMX output at ~30fps
   - Implements smooth 3-second transitions via linear interpolation
   - Methods: `start()`, `stop()`, `set_with_transition()`, `set_immediate()`, `reconfigure()`
   - Sends DMX packets directly via `_send_dmx_packet()` method (doesn't use StupidArtnet's threading)
   - Tracks real-time connection status (connected/disconnected, error messages)
   - Silently handles socket errors without console spam

4. **Integration Layer** (`app/dmx_controller.py`)
   - Wires together ConfigManager, SceneManager, and DMXController
   - Provides backward-compatible function-based API for Flask views
   - Manages global instances and initialization
   - Functions: `init_dmx_controller()`, `activate_scene()` (toggles a scene
     on/off, returns the full active list), `test_scene()`, `get_config()`,
     `save_config()`, etc.

#### Flask Application

- **Flask application factory pattern**: `create_app()` in `app/__init__.py` initializes the app with blueprints
- **Two main blueprints**:
  - `main_bp` (`app/views/main.py`): Scene activation and DMX monitoring APIs
  - `setup_bp` (`app/views/setup.py`): Configuration endpoints (network, fixtures, scenes)
- **HTTP Basic Auth**: All endpoints protected. Credentials come from
  `DMXLIFE_USERNAME`/`DMXLIFE_PASSWORD`, required when bound to a
  non-loopback host; loopback falls back to development defaults with a
  warning. See `README.md`.
- **DMX initialization**: Happens on first request via `@app.before_request`

### Configuration Storage
- **Single JSON file** (`app/config.json`): Stores all settings, fixtures, and scenes
- Read/write operations handled by `ConfigManager` class
- Integration layer provides `get_config()` and `save_config()` functions for views
- Config structure:
  ```json
  {
    "artnet_ip": "192.168.3.170",
    "artnet_port": 6454,
    "universe": 1,
    "packet_size": 512,
    "refresh_rate": 30,
    "fixtures": [{"name": "...", "type": "...", "start_channel": 1, "channel_count": 13, "linked_to": "MasterFixtureName or null"}],
    "scenes": [{"name": "...", "channels": [0-255 array], "enabledFixtures": [fixture names], "group": "exclusive-group-name, or null for additive"}]
  }
  ```

### Frontend Pattern
- **Vanilla JavaScript** (no frameworks) in `app/static/js/`:
  - `fixtures.js`: Fixture CRUD with real-time DMX channel mapping visualization
  - `scenes.js`: Scene editor with per-fixture enable/disable and slider controls
  - `network.js`: Art-Net configuration form
  - `main.js`: Scene activation interface
  - `dmx-monitor.js`: 512-channel real-time monitor (large screens only, ~10fps refresh)
- **Client-side state management**: Each JS file maintains local arrays (`fixtures`, `scenes`) loaded via fetch APIs
- **Real-time fixture linking**: When adjusting master fixture sliders in scene editor, JS automatically syncs values to linked fixtures
- **Performance optimization**: Fixture type definitions cached client-side to reduce API calls during scene editing

## Critical Patterns

### Fixture Linking System
- Fixtures can be linked to a "master" fixture of the same type via `linked_to`
  field, which holds the **master's name** (or `null`) - not an array index.
  `ConfigManager.read()` migrates legacy positional indices on load.
- **During configuration**: Changes to master fixture's type/channel count propagate to linked fixtures
- **During scene editing**: Slider changes on master automatically copy values to corresponding channels on linked fixtures
- **Prevention**: Master fixtures (with children linked to them) cannot link to others to prevent circular dependencies - enforced both client-side (the link dropdown) and server-side (`update_fixtures` in `app/views/setup.py`)
- **Visual indicators**: UI shows `(→ Master Name)` for linked fixtures and `[Master]` tag for fixtures with children
- Fixture names must be unique - a link identifies its master by name, so ambiguity would break linking

### DMX Thread Management
- Background thread started in `DMXController.start()` during first request (`@app.before_request`)
- Thread sends DMX continuously at ~30fps (not just during transitions) for real-time connection monitoring
- `current_values`/`target_values`/the transition flag are guarded by a single
  `threading.Lock` in `DMXController` - always go through `set_with_transition()`,
  `set_immediate()`, or `get_current_values()` rather than touching the
  buffers directly. The socket send happens outside the lock so a slow or
  unreachable node can't stall a writer.
- Smooth transitions: Thread interpolates from current to target over `TRANSITION_DURATION` (3.0s)
  - **Note**: Original spec called for 2 seconds; implementation uses 3 seconds
- Direct control: `set_immediate()` sets DMX immediately without transition for preview
- Connection status: Tracks Art-Net connectivity in real-time, logs connection lost/restored only once
- Socket errors: Silently handled in `_send_dmx_packet()` method, no console spam

### Scene Activation is Layered, Not Single-Scene
- Scenes toggle on/off (`SceneManager.toggle_scene(name)`), and the server
  tracks a **set** of currently active scenes, not one. Every toggle rebuilds
  the full 512-channel frame from scratch by replaying every remaining active
  layer, in activation order (later layers win on any contested channel).
  Turning a layer off therefore correctly reveals whatever the remaining
  layers still define for its channels, or 0 if nothing else claims them.
- Scenes optionally belong to a `group`. Groups in `SceneManager.EXCLUSIVE_GROUPS`
  are single-select - activating one deactivates that group's current member.
  Any other group (or no group) is additive and layers independently.
- Scenes store `enabledFixtures` array (fixture names, not indices). A
  **non-empty** list means: copy each named fixture's entire channel range
  from the scene, zeros included. An **empty** list means something different
  - a sparse overlay that writes only the scene's non-zero channels,
    ignoring fixture boundaries entirely. This is what lets a scene touch a
    handful of channels inside a fixture another active layer also controls,
    without stomping the rest of it. See [ADR-0007](../docs/adr/0007-sparse-overlay-via-empty-enabled-fixtures.md).
- Frontend checkboxes control which fixtures participate in each scene
- `DMXController.set_with_transition()` applies smooth 3-second transition
- `DMXController.set_immediate()` bypasses transition for instant preview
- `POST /api/scenes/activate` returns every currently active scene name, not
  just the one that was clicked - the frontend mirrors that list rather than
  tracking active state itself

## Key Developer Workflows

### Running the Application
```bash
./start.sh        # Start server in background (port 5050)
tail -f nohup.out # View logs
./stop.sh         # Stop server
```

Or manually with venv:
```bash
source venv/bin/activate
python app.py     # Runs on port 5050 (not 5000!)
```

### Adding New Fixture Types
1. Update `FixtureType.TYPES` dict in `app/models/fixture.py`
2. Define channels with `name`, `default`, and `visible` (hidden channels not shown in UI)
3. Example: `'ShowTec LEDPAR 56'` has 3 visible RGB channels and 3 hidden control channels

### Testing Changes
- No automated tests exist; manual testing via web UI required
- Use "Test Scene" button in scene editor for immediate DMX output validation
- Check `app/config.json` after save operations to verify persistence

## Project-Specific Conventions

### Port Configuration
- Application runs on **port 5050** (not the Flask default 5000) - see `app.py`
- Art-Net default port is 6454

### Error Handling
- Backend: Log errors via `current_app.logger.error()`, return JSON with `success: false`
- Frontend: Use `alert()` for user-facing errors (no fancy toast notifications)

### DMX Channel Indexing
- **1-based in UI/config** (user-facing "Channel 1")
- **0-based in Python arrays** (`current_dmx_values[0]` is channel 1)
- JavaScript syncs values by iterating `channels` array where index 0 = DMX channel 1

### Scene Limits
- `MAX_SCENES` in `app/__init__.py` (currently 40 - check the source, don't
  hardcode this number in docs, it has already gone stale once)
- Enforced in `save_scene()` for new scenes only (editing an existing scene
  at the limit is allowed); `GET /setup/api/config` includes `MAX_SCENES` so
  the editor UI can show remaining capacity

## Integration Points

### StupidArtnet Library
- Initialized in `load_configuration()` with `StupidArtnet(ip, universe, packet_size, fps)`
- Must call `dmx_controller.start()` before `set()` to begin broadcasting
- Use `set_simplified(False)` to control net/subnet separately

### Frontend-Backend Communication
- All APIs return JSON: `{'success': true/false, 'message': '...', <data>}`
- Scene activation: `POST /api/scenes/activate` with `{'scene': 'name'}` -
  toggles it and returns `{'success': true, 'active_scenes': [...]}` (every
  currently active scene, not just the one clicked)
- DMX monitoring: `GET /api/dmx/values` returns `{values: [...], highest_active: N, active_scene: 'most recent name or null', active_scenes: [...]}`
- Config updates: `POST /setup/api/config/<section>` with relevant data
- Test scene: `POST /setup/api/config/scenes/test` with `{'channels': [...]}`

## Common Pitfalls

- **`lib/` and `routes/` don't exist** in this codebase — don't create them or assume code lives there. `app/views/` is live, actively-maintained code (the Flask blueprints), not legacy.
- **Config reload**: After saving to `config.json` via ConfigManager, call `scene_manager.load_scenes()` or `dmx_controller.reconfigure()` as needed
- **DMX buffer access**: Go through `DMXController`'s locked methods
  (`set_with_transition()`, `set_immediate()`, `get_current_values()`) -
  never read or write `current_values`/`target_values` directly, the lock
  only protects callers who use it
- **Fixture deletion**: Links are name-based now, so deleting a fixture from
  anywhere in the list doesn't shift anyone else's `linked_to` - only links
  that named the deleted fixture need clearing, which `fixtures.js` and
  `update_fixtures` both already do automatically
- **Module imports**: Import from integration layer (`from app.dmx_controller import activate_scene`), not from class files directly

## Design Decisions vs Implementation

Some implementation details differ from the original design brief (formerly
`design/prompt.txt`, later removed - see git history):
- **Transition duration**: 3 seconds (spec: 2 seconds) - provides smoother visual effect
- **Test mode**: Immediately applies DMX without transitions for instant feedback
- **Fixture linking**: Prevents circular dependencies by blocking master fixtures from being linked
- **Connection monitoring**: Continuous DMX output (not just during transitions) enables real-time connection status tracking
- **No StupidArtnet threading**: We manage our own thread and call socket operations directly to properly track connection status

## DMX Protocol Context

- DMX channels: 1-512 per universe, each controlling one fixture function (0-255 value range)
- Art-Net: DMX over Ethernet/WiFi, default port 6454
- Fixture types vary in channel count: RGB=3ch, RGBW=4ch, Moving Head=13ch+
- Scenes: a partial or complete set of DMX values for the fixtures they
  enable - the transmitted frame is composed from every currently active
  scene layered together, not from one scene alone

## Authoritative Documentation

This file is a quick orientation, not the source of truth - it can and does
go stale. When in doubt, or for anything not covered here:
- [`docs/adr/`](../docs/adr/) - why each architectural decision was made,
  including known trade-offs and risks
- [`openspec/specs/`](../openspec/specs/) - what the system does today, as
  testable requirements
- [`openspec/changes/`](../openspec/changes/) - proposed work not yet done;
  `openspec/changes/archive/` - what has already landed
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) - module map and
  component responsibilities
