# DMX Life - Architecture Documentation

## Overview

DMX Life is built with a modular architecture following the **Single Responsibility Principle**. The codebase is organized into focused modules, each handling one specific aspect of the application.

## Core Architecture

### Module Dependency Graph

```
┌─────────────────────────────────────────────────────────┐
│                     Flask Application                    │
│                   (app/__init__.py)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ├─► Views (Blueprints)
                       │   ├─► main_bp (app/views/main.py)
                       │   └─► setup_bp (app/views/setup.py)
                       │
                       └─► DMX Integration Layer
                           (app/dmx_controller.py)
                           │
                           ├─► ConfigManager
                           │   (app/config_manager.py)
                           │
                           ├─► SceneManager
                           │   (app/scene_manager.py)
                           │
                           └─► DMXController
                               (app/dmx_controller_class.py)
                               │
                               └─► StupidArtnet (Art-Net Protocol)
```

## Component Details

### 1. ConfigManager (`app/config_manager.py`)

**Responsibility**: Configuration file I/O operations

**Key Methods**:
- `read()` - Read entire configuration from JSON
- `write(config)` - Write entire configuration to JSON
- `update(**kwargs)` - Update specific keys
- `get_network_settings()` - Get Art-Net settings
- `get_fixtures()` - Get fixture list
- `get_scenes()` - Get scene list
- `save_scene(name, channels, enabled_fixtures)` - Save/update a scene
- `delete_scene(name)` - Delete a scene
- `get_scene_by_name(name)` - Get specific scene

**Design Notes**:
- Pure data layer - no business logic
- Automatically creates default config if missing
- All file operations are exception-safe
- Logs errors through Flask's logger

**Configuration Schema**:
```json
{
  "artnet_ip": "192.168.1.100",
  "artnet_port": 6454,
  "universe": 0,
  "packet_size": 512,
  "refresh_rate": 30,
  "fixtures": [
    {
      "name": "Stage Left",
      "type": "RGB Par",
      "start_channel": 1,
      "channel_count": 3,
      "linked_to": null
    }
  ],
  "scenes": [
    {
      "name": "Warm White",
      "channels": [255, 200, 180, ...],
      "enabledFixtures": ["Stage Left", "Stage Right"]
    }
  ]
}
```

### 2. SceneManager (`app/scene_manager.py`)

**Responsibility**: Scene logic and DMX buffer construction

**Key Methods**:
- `load_scenes()` - Load scenes from config
- `get_available_scenes()` - List scene names
- `get_active_scene()` - Get currently active scene
- `get_highest_active_idx()` - Get highest used channel
- `build_dmx_buffer(scene_name, current_values)` - Build DMX buffer for scene
- `save_scene(name, channels, enabled_fixtures)` - Save scene (delegates to ConfigManager)
- `delete_scene(name)` - Delete scene (delegates to ConfigManager)

**Design Notes**:
- Caches scenes in memory for performance
- Builds DMX buffers based on enabled fixtures
- Handles selective fixture activation
- Tracks active scene state
- Preserves current values for non-enabled fixtures

**Buffer Building Algorithm**:
1. Start with current DMX values (or zeros)
2. If no fixtures enabled → activate all channels from scene
3. If fixtures enabled → iterate through fixtures:
   - Skip disabled fixtures
   - For each enabled fixture:
     - Copy channel values from scene to buffer
     - Track highest active channel index
4. Return buffer and success status

### 3. DMXController (`app/dmx_controller_class.py`)

**Responsibility**: DMX hardware communication and transitions

**Key Methods**:
- `start()` - Start DMX output thread
- `stop()` - Stop DMX output thread
- `set_with_transition(buffer)` - Set values with 3-second transition
- `set_immediate(buffer)` - Set values immediately (for testing)
- `get_current_values()` - Get current DMX values
- `get_connection_status()` - Get Art-Net connection status
- `reconfigure(...)` - Change network settings

**Design Notes**:
- Runs background thread for continuous DMX output at ~30fps
- Implements linear interpolation for smooth transitions
- Sends DMX directly via `_send_dmx_packet()` method (not StupidArtnet's `show()`)
- Thread-safe access to DMX value buffers
- Tracks connection status in real-time (connected/disconnected, last error)
- Silently handles socket errors without console spam
- Does not use StupidArtnet's internal threading

**Transition Algorithm**:
```python
# In background thread loop (~30fps)
while running:
    sleep(0.033)  # ~30fps
    
    if transition_active:
        elapsed = now - transition_start_time
        progress = min(elapsed / 3.0, 1.0)  # 0.0 to 1.0
        
        for channel in range(512):
            current = current_values[channel]
            target = target_values[channel]
            interpolated = current + (target - current) * progress
            current_values[channel] = interpolated
        
        if progress >= 1.0:
            transition_active = False
    
    # Always send DMX (for connection monitoring)
    _send_dmx_packet(current_values)
```

**Connection Status Tracking**:
```python
def _send_dmx_packet(self, buffer):
    """Send DMX with connection status tracking"""
    packet = bytearray()
    packet.extend(self.artnet.packet_header)
    packet.extend(buffer)
    
    try:
        self.artnet.socket_client.sendto(packet, (ip, port))
        
        # Handle artsync separately
        if self.artnet.if_sync:
            try:
                self.artnet.make_artsync_header()
                self.artnet.socket_client.sendto(artsync_header, (ip, port))
            except socket.error:
                pass  # Silent
        
        # Update status on success
        if not self.connection_status['connected']:
            self.connection_status['connected'] = True
            self.connection_status['error_message'] = None
            logger.info("Art-Net connection restored")
            
    except socket.error as error:
        was_connected = self.connection_status['connected']
        self.connection_status['connected'] = False
        self.connection_status['last_error_time'] = time.time()
        self.connection_status['error_message'] = str(error)
        
        # Log only once when first disconnected
        if was_connected:
            logger.warning(f"Art-Net connection lost: {error}")
    finally:
        self.artnet.sequence = (self.artnet.sequence + 1) % 256
```

### 4. Integration Layer (`app/dmx_controller.py`)

**Responsibility**: Wire components together, provide backward-compatible API

**Key Functions**:
- `init_dmx_controller(app)` - Initialize all components
- `activate_scene(name)` - Activate scene with transition
- `test_scene(channels)` - Test scene immediately
- `get_active_scene()` - Get active scene name
- `get_highest_active_idx()` - Get highest channel
- `get_available_scenes()` - List scenes
- `save_scene(...)` - Save scene
- `delete_scene(...)` - Delete scene
- `get_config()` - Get configuration
- `save_config(...)` - Save configuration
- `get_connection_status()` - Get connection status
- `get_current_dmx_values()` - Get current DMX values

**Design Notes**:
- Maintains global instances of ConfigManager, SceneManager, DMXController
- Provides function-based API for Flask views
- Handles initialization on first request
- Manages configuration reload and DMX reconfiguration
- Exports current_dmx_values for monitoring

**Initialization Flow**:
```python
@app.before_request
def before_request():
    if not hasattr(app, '_dmx_initialized'):
        # 1. Create ConfigManager
        config_manager = ConfigManager(config_file)
        
        # 2. Create SceneManager with ConfigManager
        scene_manager = SceneManager(config_manager)
        scene_manager.load_scenes()
        
        # 3. Get network settings
        network_settings = config_manager.get_network_settings()
        
        # 4. Create DMXController with settings
        dmx_controller = DMXController(
            network_settings['artnet_ip'],
            network_settings['universe'],
            network_settings['packet_size'],
            network_settings['refresh_rate']
        )
        
        # 5. Start DMX thread
        dmx_controller.start()
        
        app._dmx_initialized = True
```

## Web Layer

### Flask Application (`app/__init__.py`)

**Responsibilities**:
- Create Flask application
- Register blueprints
- Configure HTTP Basic Auth
- Initialize DMX controller

**Configuration**:
- `SECRET_KEY` - Random 24-byte key
- `CONFIG_FILE` - Path to config.json
- `MAX_SCENES` - Maximum 10 scenes

### View Blueprints

#### Main Blueprint (`app/views/main.py`)

**Routes**:
- `GET /` - Main scene selection page
- `GET /api/scenes` - List available scenes
- `POST /api/scenes/activate` - Activate a scene
- `GET /api/dmx/values` - Get current DMX values (for monitor)
- `GET /api/connection/status` - Get Art-Net connection status

#### Setup Blueprint (`app/views/setup.py`)

**Routes**:
- `GET /setup/` - Setup main page
- `GET /setup/network` - Network configuration page
- `GET /setup/fixtures` - Fixture configuration page
- `GET /setup/scenes` - Scene editor page
- `GET /setup/api/config` - Get configuration
- `POST /setup/api/config/network` - Update network settings
- `POST /setup/api/config/fixtures` - Update fixtures
- `POST /setup/api/config/scenes` - Save scene
- `DELETE /setup/api/config/scenes` - Delete scene
- `POST /setup/api/config/scenes/test` - Test scene
- `GET /setup/api/fixture-types` - Get fixture types
- `GET /setup/api/fixture-types/<type>` - Get fixture type details

## Frontend Architecture

### JavaScript Modules

Each page has its own JavaScript file with **no shared state**:

1. **main.js** - Scene activation interface
   - Loads scene list via API
   - Activates scenes on button click
   - Shows active scene indicator

2. **network.js** - Network configuration
   - Form validation
   - Submits network settings
   - Shows success/error alerts

3. **fixtures.js** - Fixture management
   - CRUD operations for fixtures
   - Real-time DMX channel mapping visualization
   - Detects channel conflicts
   - Handles fixture linking UI

4. **scenes.js** - Scene editor
   - Scene CRUD operations
   - Per-fixture enable/disable checkboxes
   - Slider controls for each channel
   - Real-time linked fixture synchronization
   - Test scene button (immediate feedback)

5. **dmx-monitor.js** - DMX channel monitor
   - Polls `/api/dmx/values` at ~10fps
   - Displays all 512 channels
   - Shows active scene and highest channel
   - Large screen only

### Client-Side Fixture Linking

When a user adjusts a slider on a master fixture:
1. JavaScript detects the change
2. Finds all fixtures linked to this master
3. Calculates corresponding channel for each linked fixture
4. Updates slider values in real-time
5. Values are saved when scene is saved

## Data Flow

### Scene Activation Flow

```
User clicks scene button
         ↓
Frontend: POST /api/scenes/activate
         ↓
View: activate_scene_endpoint()
         ↓
Integration: activate_scene(name)
         ↓
SceneManager: build_dmx_buffer(name)
         ├─► ConfigManager: get_scene_by_name()
         ├─► ConfigManager: get_fixtures()
         └─► Returns DMX buffer (bytearray(512))
         ↓
DMXController: set_with_transition(buffer)
         ├─► Sets target_values = buffer
         ├─► Starts transition (transition_active = True)
         └─► Background thread interpolates over 3 seconds
         ↓
StupidArtnet: Continuous output at ~30fps
         ↓
Art-Net → DMX Fixtures
```

### Configuration Save Flow

```
User saves network settings
         ↓
Frontend: POST /setup/api/config/network
         ↓
View: update_network_config()
         ↓
Integration: save_config(network_config)
         ↓
ConfigManager: update(**kwargs)
         ├─► Read config.json
         ├─► Update keys
         └─► Write config.json
         ↓
DMXController: reconfigure()
         ├─► Stop thread
         ├─► Recreate StupidArtnet
         └─► Restart thread
```

## Threading Model

### DMX Output Thread

**Purpose**: Continuous DMX output and smooth transitions

**Lifecycle**:
1. Started on first HTTP request
2. Runs until application shutdown
3. Daemon thread (exits when main thread exits)

**Loop** (~30fps):
```python
while running:
    sleep(0.033)  # ~30ms
    
    if transition_active:
        update_transition()  # Interpolate values
        
    artnet.set(current_values)  # Send DMX packet
```

**Thread Safety**:
- `current_values` - Read by thread, written by main thread (during immediate set)
- `target_values` - Read by thread, written by main thread
- `transition_active` - Read/written by both (boolean, atomic)
- `transition_start_time` - Written by main, read by thread

## Key Design Decisions

### Why Port 5050?
Flask's default port 5000 is commonly used by other services (AirPlay on macOS). Port 5050 avoids conflicts.

### Why 3-Second Transitions?
Original spec called for 2 seconds, but 3 seconds provides smoother visual effect for human perception.

### Why Monkey-Patch StupidArtnet?
StupidArtnet prints "ERROR: Socket error" to console when network is unreachable. This creates spam in logs. Monkey-patching suppresses these while maintaining connection status tracking.

### Why Global Instances?
Flask views need access to DMX controller. Global instances simplify access without complex dependency injection. The integration layer provides a clean API.

### Why Three Separate Modules?
Original `dmx_controller.py` was 434 lines with mixed responsibilities. Splitting into ConfigManager, SceneManager, and DMXController:
- Reduces complexity (each ~150-200 lines)
- Improves testability (can mock components)
- Eases maintenance (bugs easier to locate)
- Enables extensibility (easy to add features)

### Why Direct Socket Calls Instead of StupidArtnet's show()?
StupidArtnet's `show()` method:
- Prints "ERROR: Socket error" to console (can't be suppressed)
- Starts its own thread when `start()` is called
- Doesn't provide connection status feedback

Our approach:
- Direct socket calls in `_send_dmx_packet()` method
- Full control over error handling (silent or logged once)
- Real-time connection status tracking
- Single managed thread for all DMX output

### Why Continuous DMX Output?
Sending DMX continuously (not just during transitions) enables:
- Real-time connection status monitoring
- Immediate detection when Art-Net device goes offline/online
- Consistent DMX output even when scenes aren't changing
- Standard Art-Net behavior (devices expect continuous packets)

### Why Fixture Linking?
Users often have multiple identical fixtures. Linking allows:
- Bulk configuration changes
- Real-time value synchronization in scene editor
- Reduced setup time

## Performance Considerations

### DMX Output Rate
- Thread updates at ~30fps (0.033s sleep)
- StupidArtnet configured with `refresh_rate` parameter (default 30)
- Balance between smooth output and CPU usage

### Scene Loading
- Scenes cached in memory in SceneManager
- Config file only read when explicitly reloading
- Reduces disk I/O during scene activation

### DMX Monitor Polling
- Frontend polls at ~10fps (100ms interval)
- Only active when monitor visible
- Returns only active channels (up to highest_active_idx)
- Reduces bandwidth and parsing time

### Configuration File Size
- JSON file small (<100KB typical)
- 10 scene limit prevents unbounded growth
- Fast read/write operations

## Security

### HTTP Basic Auth
- All endpoints protected with username/password
- Default credentials: admin/banana123
- **TODO**: Make credentials configurable
- **TODO**: Add HTTPS support for production

### Input Validation
- Channel values: 0-255 (enforced in frontend and backend)
- DMX channels: 1-512 (enforced in frontend)
- Scene names: Required, non-empty
- Fixture names: Required, non-empty

### Error Handling
- Backend: Try/except blocks with logging
- Frontend: Alert dialogs for user errors
- No sensitive information in error messages

## Testing Strategy

### Manual Testing Workflow
1. Start server with `./start.sh`
2. Access http://localhost:5050
3. Configure network settings
4. Add test fixtures
5. Create test scenes
6. Activate scenes and verify DMX output
7. Check logs in `nohup.out`

### Key Test Scenarios
- Scene activation with smooth transition
- Scene testing (immediate mode)
- Fixture linking behavior
- Configuration persistence (restart server)
- Network error handling (unreachable Art-Net device)
- Channel conflict detection
- Maximum scene limit

## Future Architecture Improvements

### Potential Enhancements
1. **Database Backend**: Replace JSON with SQLite for better concurrency
2. **WebSocket Updates**: Real-time scene activation status
3. **Plugin System**: Custom fixture types without code changes
4. **API Versioning**: `/api/v1/` for backward compatibility
5. **Unit Tests**: Pytest suite for core components
6. **Docker Container**: Simplified deployment
7. **Configuration UI**: Change admin password without code
8. **Logging System**: Structured logging with rotation

### Scalability Considerations
- Current design: Single DMX controller, one universe (512 channels)
- Multiple universes: Requires multiple StupidArtnet instances
- Multiple controllers: Requires controller abstraction layer
- Web scaling: Flask development server → Gunicorn/uWSGI

## Troubleshooting

### Common Issues

**Server won't start - "Address already in use"**
- Check for running processes: `lsof -i :5050`
- Kill old process: `kill $(cat dmx_life.pid)` or `./stop.sh`

**No DMX output**
- Check Art-Net IP address in network settings
- Verify DMX fixtures are powered on
- Check connection status: `GET /api/connection/status`
- Verify fixture channel assignments don't overlap

**Scenes not saving**
- Check `config.json` file permissions
- Verify max scene limit (10) not exceeded
- Check logs in `nohup.out` for errors

**Transition not smooth**
- Verify `refresh_rate` in config (default 30)
- Check system CPU load
- Ensure DMX thread is running (check logs)

## Conclusion

DMX Life's architecture emphasizes simplicity, modularity, and maintainability. The clear separation of concerns makes the codebase easy to understand and modify. Future enhancements can be added incrementally without major refactoring.
