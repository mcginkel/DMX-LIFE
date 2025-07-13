# DMX Life - Lighting Scene Controller

DMX Life is a simple web-based application for controlling DMX lighting fixtures via multiple interfaces including Art-Net protocol over a network and USB-DMX devices. The application allows you to:

- Define DMX fixtures and their channel assignments
- Create up to 10 lighting scenes
- Selectively enable/disable fixtures in each scene
- Quickly switch between scenes with a simple interface
- Choose between Art-Net (network) and USB-DMX interfaces

## Features

- **Simple Web Interface**: Control your lighting from any device with a browser
- **Multiple DMX Interfaces**: Support for both Art-Net (network) and USB-DMX connections
- **Art-Net Protocol**: Industry standard for DMX over Ethernet/WiFi
- **USB-DMX Support**: Direct connection to USB DMX interfaces (Enttec, FTDI-based devices)
- **Auto-Detection**: Automatic detection of USB-DMX devices
- **Fixture Setup**: Configure different types of DMX fixtures (RGB, RGBW, Moving Heads, etc.)
- **Fixture Linking**: Link fixtures of the same type to automatically sync configuration changes
- **Real-time Value Sync**: Linked fixtures automatically receive matching channel values when adjusting sliders
- **Scene Designer**: Create and save lighting scenes with selective fixture control
- **Visual DMX Mapping**: See which DMX channels are assigned to which fixtures
- **Fixture Selection**: Choose which fixtures participate in each scene
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
   python app.py
   ```

5. Open a web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Setup Instructions

## System Requirements

- Python 3.7+
- Network connection to DMX fixtures via Art-Net **OR** USB-DMX interface device
- Modern web browser

### USB-DMX Device Compatibility

This application supports common USB-DMX interfaces including:
- Enttec Open DMX USB
- FTDI-based DMX interfaces
- DMXking ultraDMX
- Most generic USB-to-DMX converters

**Note**: For USB-DMX support, the `pyserial` library is required and should be automatically installed via requirements.txt.

## Interface Setup

### Choosing Your DMX Interface

DMX Life supports two types of DMX interfaces:

1. **Art-Net (Network)**: Send DMX data over Ethernet/WiFi using the Art-Net protocol
2. **USB-DMX**: Direct connection to a USB DMX interface device

### 1. Interface Configuration

Go to "Setup" -> "Interface Setup" to configure your DMX interface:

#### Art-Net Configuration:
- Select "Art-Net" as your interface type
- Enter the Art-Net IP address (use 255.255.255.255 for broadcast)
- Set the Universe and other parameters
- Click "Save Settings"

#### USB-DMX Configuration:
- Select "USB-DMX" as your interface type
- Choose your USB port (auto-detection available)
- Adjust baud rate if needed (usually 250000 for standard DMX)
- Configure advanced settings if required
- Click "Save Settings"

The application will automatically switch between interface types and restart the DMX output when you change the interface configuration.

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

- Built with Flask (Python web framework)
- Uses StupidArtnet library for Art-Net protocol
- Uses PySerial library for USB-DMX communication
- Pluggable DMX interface architecture supporting multiple hardware types
- Responsive design works on desktop and mobile devices

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, feature requests, or contributions, please open an issue on GitHub or contact the project maintainer.
