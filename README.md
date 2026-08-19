# DMX Life - Lighting Scene Controller

DMX Life is a simple web-based application for controlling DMX lighting fixtures via Art-Net protocol over a network. The application allows you to:

- Define DMX fixtures and their channel assignments
- Create a configurable number of lighting scenes, organized into groups
- Selectively enable/disable fixtures in each scene
- Layer scenes from different groups together, toggling each on and off independently

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

4. Set operator credentials. `start.sh` binds the server to all network
   interfaces (`0.0.0.0`) so devices on the venue network can reach it, and
   the application refuses to start that way without credentials configured:
   ```bash
   cp .env.example .env
   # edit .env and set DMXLIFE_USERNAME / DMXLIFE_PASSWORD
   ```
   `.env` is gitignored and stays on this machine only.

   For local development on `127.0.0.1` only, this step can be skipped — the
   application falls back to development credentials (`admin` / `banana123`)
   and warns that it's doing so. That fallback only ever applies on loopback;
   it is refused outright on any other bind address.

5. Run the application:
   ```bash
   ./start.sh
   ```

   Or manually (binds to loopback only, so `.env` isn't required):
   ```bash
   source venv/bin/activate
   python app.py
   ```

6. Stop the application:
   ```bash
   ./stop.sh
   ```

7. Open a web browser and navigate to:
   ```
   http://localhost:5050
   ```

   Sign in with the credentials set in `.env` (or the development defaults, if
   running on loopback without one).

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

Finally, use the main interface to activate your scenes. Scenes are organized
into groups (which groups exist and their labels come from each scene's
`group`, set when it was created):

- **Exclusive groups** (e.g. a "main look" group, a "background colour"
  group) — clicking a scene there replaces whichever scene in that same
  group was active, so only one member of the group is ever active at once.
- **Additive scenes** (no group, or a group that isn't exclusive) — these
  layer on top of whatever else is active without displacing anything.

Any active scene can be turned off again by clicking it a second time — the
system rebuilds the DMX output from whatever scenes remain active, so turning
one off correctly reveals what's underneath rather than leaving stale values
or blacking out fixtures other scenes still claim. Only fixtures a scene
enables are affected by it; everything else is left as other active scenes
(or nothing) leave it.

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
│   ├── config_manager.py        # Configuration file I/O (atomic writes)
│   ├── scene_manager.py         # Scene layering & DMX frame composition
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
├── design/                      # Design documentation (orientation)
├── docs/adr/                    # Architecture decision records
├── openspec/                    # Behavioural specs & change proposals
├── start.sh                     # Start server in background
├── stop.sh                      # Stop server
├── app.py                       # Application entry point
└── requirements.txt             # Python dependencies
```

### Code Architecture

See [`design/ARCHITECTURE.md`](design/ARCHITECTURE.md) for the module map and
component responsibilities, [`docs/adr/`](docs/adr/) for why things are built
the way they are, and [`openspec/specs/`](openspec/specs/) for what the
system does, in testable terms.

### Running in Development

```bash
# Start server (runs in background)
./start.sh

# View logs
tail -f nohup.out

# Stop server
./stop.sh
```

## Documentation

- [`design/ARCHITECTURE.md`](design/ARCHITECTURE.md) — module map and component
  responsibilities, an orientation guide rather than a full reference.
- [`docs/adr/`](docs/adr/) — architecture decision records: what was decided,
  why, and what trade-off it costs. Start here for "why does it work this
  way" questions.
- [`openspec/specs/`](openspec/specs/) — behavioural specifications: what the
  system does, in testable scenarios. `openspec/changes/` holds proposals for
  known gaps not yet addressed, and `openspec/changes/archive/` holds ones
  already landed.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, feature requests, or contributions, please open an issue on GitHub or contact the project maintainer.
