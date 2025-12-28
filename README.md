# DMX Life - Lighting Scene Controller

DMX Life is a simple web-based application for controlling DMX lighting fixtures via Art-Net protocol over a network. The application allows you to:

- Define DMX fixtures and their channel assignments
- Create up to 10 lighting scenes
- Selectively enable/disable fixtures in each scene
- Quickly switch between scenes with a simple interface

## Features

- **Simple Web Interface**: Control your lighting from any device with a browser
- **Art-Net Protocol**: Industry standard for DMX over Ethernet/WiFi
- **Real-time Connection Status**: Visual indicator shows Art-Net device connectivity
- **Fixture Setup**: Configure different types of DMX fixtures (RGB, RGBW, Moving Heads, etc.)
- **Fixture Linking**: Link fixtures of the same type to automatically sync configuration changes
- **Real-time Value Sync**: Linked fixtures automatically receive matching channel values when adjusting sliders
- **Scene Designer**: Create and save lighting scenes with selective fixture control
- **Visual DMX Mapping**: See which DMX channels are assigned to which fixtures
- **Fixture Selection**: Choose which fixtures participate in each scene
- **Smooth Transitions**: 3-second fade between scenes for professional look
- **On-Demand DMX Monitor**: Real-time visualization of all 512 DMX channel values (available on large screens when requested)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dmx-life.git
   cd dmx-life
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   source venv/bin/activate
   python app.py
   ```

5. Stop the application:
   ```bash
   ./stop.sh
   ```

6. Open a web browser and navigate to:
   ```
   http://localhost:5050
   ```
   
   Default credentials:
   - Username: `admin`
   - Password: `banana123`

## Setup Instructions

### 1. Network Configuration

First, configure the Art-Net network settings:
- Go to "Setup" -> "Network Setup"
- Enter the Art-Net IP address (use 255.255.255.255 for broadcast)
- Set the Universe and other parameters
- Click "Save Network Settings"

### 2. Fixture Configuration

Next, define your DMX fixtures:
- Go to "Setup" -> "Fixture Setup"
- Click "Add New Fixture"
- Enter a name, select fixture type, and set starting DMX channel
- **Optional**: Link the fixture to another fixture of the same type
  - Select a fixture from the "Link to Fixture" dropdown
  - Linked fixtures will automatically copy certain changes from the master fixture
  - A fixture that has others linked to it cannot be linked to another fixture (prevents loops)
- Click "Save Fixture"
- Repeat for all your fixtures

**Fixture Linking Feature**: When fixtures are linked, changes to the master fixture's type and channel configuration will automatically propagate to all linked fixtures. This is useful when you have multiple identical fixtures that should maintain the same configuration. The visual fixture list shows linked relationships with arrows (→) and marks master fixtures with [Master].

**Real-time Value Synchronization**: During scene editing, when you adjust a channel slider on a master fixture, all linked fixtures of the same type will automatically receive the same value on their corresponding channels. This makes it easy to control multiple identical fixtures simultaneously - simply adjust one fixture and all linked fixtures will follow in real-time.

### 3. Scene Creation

Create lighting scenes:
- Go to "Setup" -> "Scene Setup"
- Click "Create New Scene"
- Enter a scene name
- Enable or disable fixtures you want to include in this scene
- Adjust the sliders for each enabled fixture's channels
- **Linked Fixture Control**: When you adjust a slider on a master fixture, all linked fixtures of the same type will automatically receive the same value on their corresponding channels in real-time
- Click "Test Scene" to preview
- Click "Save Scene" when finished

### 4. Scene Control

Finally, use the main interface to activate your scenes:
- Go to "Scenes" page
- Click on any scene to activate it
- Only enabled fixtures in that scene will respond

### 5. DMX Monitor (Optional)

On larger screens, you can view real-time DMX channel data:
- Look for the "Show Monitor" button on the main scenes page
- Click it to display a live view of all 512 DMX channel values
- The monitor updates at approximately 10fps to show current channel states
- Click "Hide Monitor" to close the monitor and stop polling

## System Requirements

- Python 3.7+
- Network connection to DMX fixtures via Art-Net
- Modern web browser

## Technical Details

### Architecture

DMX Life uses a modular architecture with clear separation of concerns:

- **Flask Web Framework**: Powers the backend and web interface
- **StupidArtnet Library**: Provides Art-Net protocol communication with silent error handling
- **Modular Code Structure**:
  - `app/config_manager.py` - Handles all configuration file I/O operations
  - `app/scene_manager.py` - Manages scene logic and DMX buffer building
  - `app/dmx_controller_class.py` - Controls DMX hardware and smooth transitions
  - `app/dmx_controller.py` - Integration layer providing backward-compatible API
  - `app/views/main.py` - Scene activation and monitoring endpoints
  - `app/views/setup.py` - Configuration endpoints

### Key Features

- **Smooth Scene Transitions**: 3-second linear interpolation between scenes
- **Real-time DMX Output**: Background thread sends DMX data at ~30fps
- **Connection Monitoring**: Tracks Art-Net connection status with automatic error suppression
- **Configuration Persistence**: All settings stored in `app/config.json`
- **HTTP Basic Authentication**: Protected endpoints with username/password
- **Responsive Design**: Works on desktops, tablets, and mobile devices

## Development

### Project Structure

```
DMX-LIFE/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.json              # Configuration storage
│   ├── config_manager.py        # Configuration file I/O
│   ├── scene_manager.py         # Scene logic & buffer building
│   ├── dmx_controller_class.py  # DMX hardware control
│   ├── dmx_controller.py        # Integration layer
│   ├── models/
│   │   └── fixture.py           # Fixture type definitions
│   ├── views/
│   │   ├── main.py              # Scene activation endpoints
│   │   └── setup.py             # Configuration endpoints
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
├── design/                      # Design documentation
├── start.sh                     # Start server in background
├── stop.sh                      # Stop server
├── app.py                       # Application entry point
└── requirements.txt             # Python dependencies
```

### Code Architecture

The application follows a **modular architecture** with clear separation of concerns:

1. **ConfigManager** (`config_manager.py`)
   - Handles all JSON configuration file operations
   - Methods: `read()`, `write()`, `update()`, `save_scene()`, `delete_scene()`
   - No business logic, just data persistence

2. **SceneManager** (`scene_manager.py`)
   - Manages scene state and logic
   - Builds DMX buffers based on enabled fixtures
   - Tracks active scene and highest active channel

3. **DMXController** (`dmx_controller_class.py`)
   - Controls StupidArtnet hardware interface
   - Manages background thread for continuous DMX output
   - Implements smooth 3-second transitions via linear interpolation
   - Provides immediate mode for scene testing
   - Silently handles socket errors when Art-Net device unreachable

4. **Integration Layer** (`dmx_controller.py`)
   - Wires together ConfigManager, SceneManager, and DMXController
   - Provides backward-compatible API for views
   - Exports global instances for easy access

### Running in Development

```bash
# Start server (runs in background)
./start.sh

# View logs
tail -f nohup.out

# Stop server
./stop.sh
```

### Key Design Decisions

- **Port 5050**: Application runs on port 5050 (not Flask's default 5000)
- **3-Second Transitions**: Provides smooth visual effect (original spec called for 2 seconds)
- **Background DMX Thread**: Continuous output at ~30fps ensures stable lighting
- **Silent Socket Errors**: StupidArtnet monkey-patched to suppress console spam when network unavailable
- **Fixture Linking**: Prevents circular dependencies by blocking master fixtures from being linked

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, feature requests, or contributions, please open an issue on GitHub or contact the project maintainer.
