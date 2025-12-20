# DMX Life - Copilot Instructions

## Project Overview
DMX Life is a Flask web application for controlling DMX lighting fixtures via Art-Net protocol. Users create lighting scenes with selective fixture control and activate them through a simple web interface.

**Design Philosophy**: Built for non-technical users with focus on simplicity and intuitive controls. See `design/prompt.txt` for original requirements and design rationale.

## Architecture

### Backend Structure
- **Flask application factory pattern**: `create_app()` in `app/__init__.py` initializes the app with blueprints
- **Two main blueprints**:
  - `main_bp` (`app/views/main.py`): Scene activation and DMX monitoring APIs
  - `setup_bp` (`app/views/setup.py`): Configuration endpoints (network, fixtures, scenes)
- **DMX controller** (`app/dmx_controller.py`): Global singleton managing Art-Net output via background thread
  - Runs continuous DMX output at ~30fps
  - Implements 3-second smooth transitions between scenes using linear interpolation
  - `test_scene()` bypasses transitions for immediate feedback
  - Exports `current_dmx_values` bytearray for real-time monitoring

### Configuration Storage
- **Single JSON file** (`app/config.json`): Stores all settings, fixtures, and scenes
- Read/write operations in `dmx_controller.py` via `get_config()` and `save_config()`
- Config structure:
  ```json
  {
    "artnet_ip": "192.168.3.170",
    "universe": 1,
    "fixtures": [{"name": "...", "type": "...", "start_channel": 1, "channel_count": 13, "linked_to": null}],
    "scenes": [{"name": "...", "channels": [0-255 array], "enabledFixtures": [fixture indices]}]
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
- Background thread started in `start_dmx_thread()` during first request (`@app.before_request`)
- Thread-safe access to global `current_dmx_values` and `target_dmx_values` bytearrays
- Smooth transitions: Thread interpolates from current to target over `TRANSITION_DURATION` (3.0s)
  - **Note**: Original spec called for 2 seconds; implementation uses 3 seconds
- Direct control: `test_scene()` sets DMX immediately without transition for preview

### Scene Activation with Selective Fixtures
- Scenes store `enabledFixtures` array (fixture indices)
- `activate_scene()` only sets DMX channels for enabled fixtures; others remain at 0
- Frontend checkboxes control which fixtures participate in each scene

## Key Developer Workflows

### Running the Application
```bash
source venv/bin/activate  # Activate venv first
python app.py             # Runs on port 5050 (not 5000!)
```
Or use `./start.sh` which handles venv activation.

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

## Common Pitfalls

- **Don't modify `lib/`, `routes/`, `views/` folders**: These are legacy/unused directories from earlier design iterations
- **Config reload**: After saving to `config.json`, call `load_configuration()` to reload DMX controller
- **Thread safety**: Only modify `target_dmx_values` from main thread; DMX thread reads it for interpolation
- **Fixture index shifts**: When deleting fixtures, manually update `linked_to` indices and `enabledFixtures` in all scenes (not currently automated)

## Design Decisions vs Implementation

Some implementation details differ from original spec (`design/prompt.txt`):
- **Transition duration**: 3 seconds (spec: 2 seconds) - provides smoother visual effect
- **Test mode**: Immediately applies DMX without transitions for instant feedback
- **Fixture linking**: Prevents circular dependencies by blocking master fixtures from being linked

## DMX Protocol Context

- DMX channels: 1-512 per universe, each controlling one fixture function (0-255 value range)
- Art-Net: DMX over Ethernet/WiFi, default port 6454
- Fixture types vary in channel count: RGB=3ch, RGBW=4ch, Moving Head=13ch+
- Scenes: Collections of DMX values representing complete lighting states
