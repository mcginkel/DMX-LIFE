# DMX Life - Copilot Instructions

## Project Overview
DMX Life is a Flask web application for controlling DMX lighting fixtures via Art-Net protocol. Users create lighting scenes with selective fixture control and activate them through a simple web interface.

**Design Philosophy**: Built for non-technical users with focus on simplicity and intuitive controls. See `design/prompt.txt` for original requirements and design rationale.

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
   - Manages scene state and logic
   - Builds DMX buffers based on enabled fixtures
   - Methods: `load_scenes()`, `build_dmx_buffer()`, `get_active_scene()`, etc.
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
   - Functions: `init_dmx_controller()`, `activate_scene()`, `test_scene()`, `get_config()`, `save_config()`, etc.

#### Flask Application

- **Flask application factory pattern**: `create_app()` in `app/__init__.py` initializes the app with blueprints
- **Two main blueprints**:
  - `main_bp` (`app/views/main.py`): Scene activation and DMX monitoring APIs
  - `setup_bp` (`app/views/setup.py`): Configuration endpoints (network, fixtures, scenes)
- **HTTP Basic Auth**: All endpoints protected (default: admin/banana123)
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
    "fixtures": [{"name": "...", "type": "...", "start_channel": 1, "channel_count": 13, "linked_to": null}],
    "scenes": [{"name": "...", "channels": [0-255 array], "enabledFixtures": [fixture names]}]
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
- Fixtures can be linked to a "master" fixture of the same type via `linked_to` field (fixture index or null)
- **During configuration**: Changes to master fixture's type/channel count propagate to linked fixtures
- **During scene editing**: Slider changes on master automatically copy values to corresponding channels on linked fixtures
- **Prevention**: Master fixtures (with children linked to them) cannot link to others to prevent circular dependencies
- **Visual indicators**: UI shows `(→ Master Name)` for linked fixtures and `[Master]` tag for fixtures with children

### DMX Thread Management
- Background thread started in `DMXController.start()` during first request (`@app.before_request`)
- Thread sends DMX continuously at ~30fps (not just during transitions) for real-time connection monitoring
- Thread-safe access to `current_values` and `target_values` bytearrays
- Smooth transitions: Thread interpolates from current to target over `TRANSITION_DURATION` (3.0s)
  - **Note**: Original spec called for 2 seconds; implementation uses 3 seconds
- Direct control: `set_immediate()` sets DMX immediately without transition for preview
- Connection status: Tracks Art-Net connectivity in real-time, logs connection lost/restored only once
- Socket errors: Silently handled in `_send_dmx_packet()` method, no console spam

### Scene Activation with Selective Fixtures
- Scenes store `enabledFixtures` array (fixture names, not indices)
- `SceneManager.build_dmx_buffer()` only sets DMX channels for enabled fixtures; others remain at current value
- Frontend checkboxes control which fixtures participate in each scene
- `DMXController.set_with_transition()` applies smooth 3-second transition
- `DMXController.set_immediate()` bypasses transition for instant preview

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
- Hard-coded `MAX_SCENES = 10` in `app/__init__.py`
- Enforced in `save_scene()` and validated in setup UI scene counter

## Integration Points

### StupidArtnet Library
- Initialized in `load_configuration()` with `StupidArtnet(ip, universe, packet_size, fps)`
- Must call `dmx_controller.start()` before `set()` to begin broadcasting
- Use `set_simplified(False)` to control net/subnet separately

### Frontend-Backend Communication
- All APIs return JSON: `{'success': true/false, 'message': '...', <data>}`
- Scene activation: `POST /api/scenes/activate` with `{'scene': 'name'}`
- DMX monitoring: `GET /api/dmx/values` returns `{values: [...], highest_active: N, active_scene: 'name'}`
- Config updates: `POST /setup/api/config/<section>` with relevant data
- Test scene: `POST /setup/api/config/scenes/test` with `{'channels': [...]}`

## Common Pitfalls

- **Don't modify `lib/`, `routes/`, `views/` folders**: These are legacy/unused directories from earlier design iterations
- **Config reload**: After saving to `config.json` via ConfigManager, call `scene_manager.load_scenes()` or `dmx_controller.reconfigure()` as needed
- **Thread safety**: Only modify `target_values` from main thread; DMX thread reads it for interpolation
- **Fixture index shifts**: When deleting fixtures, manually update `linked_to` indices and `enabledFixtures` in all scenes (not currently automated)
- **Module imports**: Import from integration layer (`from app.dmx_controller import activate_scene`), not from class files directly

## Design Decisions vs Implementation

Some implementation details differ from original spec (`design/prompt.txt`):
- **Transition duration**: 3 seconds (spec: 2 seconds) - provides smoother visual effect
- **Test mode**: Immediately applies DMX without transitions for instant feedback
- **Fixture linking**: Prevents circular dependencies by blocking master fixtures from being linked
- **Connection monitoring**: Continuous DMX output (not just during transitions) enables real-time connection status tracking
- **No StupidArtnet threading**: We manage our own thread and call socket operations directly to properly track connection status

## DMX Protocol Context

- DMX channels: 1-512 per universe, each controlling one fixture function (0-255 value range)
- Art-Net: DMX over Ethernet/WiFi, default port 6454
- Fixture types vary in channel count: RGB=3ch, RGBW=4ch, Moving Head=13ch+
- Scenes: Collections of DMX values representing complete lighting states
