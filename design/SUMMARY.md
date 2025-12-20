# DMX Life - Project Summary

## Overview

DMX Life is a Python web application for controlling DMX lighting fixtures over Art-Net protocol. It provides a simple user interface for creating and activating lighting scenes.

## Features

1. **Simple Scene Interface**
   - Easy activation of lighting scenes with a single click
   - Visual representation of scenes
   - Real-time feedback of active scene

2. **Setup Mode** with three main sections:
   - **Network Setup**: Configure Art-Net parameters (IP, port, universe)
   - **Fixture Setup**: Add and configure DMX fixtures with visual DMX map
   - **Scene Editor**: Create and test lighting scenes with intuitive sliders
     - Selectively enable/disable fixtures in each scene
     - Fine-grained DMX channel control with sliders
     - Real-time scene preview

3. **Flexible Fixture Support**
   - Support for common fixture types (RGB, RGBW, Moving Heads, etc.)
   - Visual indication of DMX channel assignment
   - Detection of channel conflicts
   - Selective fixture activation per scene

## Technical Details

### Architecture

DMX Life uses a **modular architecture** with clear separation of concerns:

#### Core Components

1. **ConfigManager** (`app/config_manager.py`)
   - Handles all JSON configuration file I/O
   - Provides methods for reading/writing network settings, fixtures, and scenes
   - Ensures configuration file exists with sensible defaults
   - No business logic - pure data persistence layer

2. **SceneManager** (`app/scene_manager.py`)
   - Manages scene state (active scene, highest active channel)
   - Builds DMX buffers based on scene configuration and enabled fixtures
   - Caches scenes for performance
   - Delegates persistence to ConfigManager

3. **DMXController** (`app/dmx_controller_class.py`)
   - Controls StupidArtnet hardware interface
   - Manages background thread for continuous DMX output (~30fps)
   - Implements smooth 3-second transitions via linear interpolation
   - Provides immediate mode for scene testing (bypasses transitions)
   - Tracks connection status in real-time via direct socket operations
   - Silently handles socket errors without console spam
   - Does not use StupidArtnet's internal threading

4. **Integration Layer** (`app/dmx_controller.py`)
   - Wires together the three core components
   - Provides backward-compatible API for Flask views
   - Manages global instances and initialization
   - Handles configuration reload and DMX reconfiguration

#### Web Layer

- **Flask Application Factory** (`app/__init__.py`)
  - Creates and configures Flask app
  - Registers blueprints for main and setup views
  - Initializes HTTP Basic Auth
  - Sets up DMX controller on first request

- **View Blueprints**
  - `app/views/main.py` - Scene activation, DMX monitoring, connection status
  - `app/views/setup.py` - Network config, fixture management, scene editor

- **Frontend**
  - Vanilla JavaScript (no frameworks)
  - Real-time fixture linking and value synchronization
  - Client-side state management
  - DMX channel visualization

#### Key Technologies

- **Flask Web Framework**: Powers the backend and web interface
- **StupidArtnet Library**: Provides Art-Net protocol communication (monkey-patched for silent errors)
- **HTTP Basic Auth**: Username/password protection (default: admin/banana123)
- **Threading**: Background DMX output thread with smooth transitions
- **JSON Configuration**: Single `config.json` file stores all settings

#### Design Patterns

- **Factory Pattern**: Flask app creation
- **Singleton Pattern**: Global DMX controller instance
- **Separation of Concerns**: Each module has one clear responsibility
- **Linear Interpolation**: Smooth transitions between scenes over 3 seconds
- **Monkey Patching**: StupidArtnet.show() overridden to suppress socket errors

## Running the Application

1. Start the application (background mode):
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   source venv/bin/activate
   python app.py
   ```

2. Stop the application:
   ```bash
   ./stop.sh
   ```

3. Access the web interface:
   ```
   http://localhost:5050
   ```
   
   Default credentials:
   - Username: `admin`
   - Password: `banana123`

4. Setup Workflow:
   - First, configure network settings (Setup → Network Setup)
   - Next, add your DMX fixtures (Setup → Fixture Setup)
   - Finally, create lighting scenes with desired fixture combinations (Setup → Scene Setup)
   - Return to the main page to activate scenes

5. View logs:
   ```bash
   tail -f nohup.out
   ```

## Future Improvements

- Additional fixture types and profiles
- Scene grouping and categories
- Scheduled scene activation
- Scene transition effects (fade styles beyond linear)
- Timeline-based scene sequencing
- Support for multiple DMX universes
- Multi-user support with role-based permissions
- Scene recording from live DMX input
- Backup/restore configuration
- Mobile app for remote control
- Integration with smart home systems
