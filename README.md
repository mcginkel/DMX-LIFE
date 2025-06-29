# DMX Life - Lighting Scene Controller

DMX Life is a simple web-based application for controlling DMX lighting fixtures via Art-Net protocol over a network. The application allows you to:

- Define DMX fixtures and their channel assignments
- Create up to 10 lighting scenes
- Selectively enable/disable fixtures in each scene
- Quickly switch between scenes with a simple interface

## Features

- **Simple Web Interface**: Control your lighting from any device with a browser
- **Art-Net Protocol**: Industry standard for DMX over Ethernet/WiFi
- **Fixture Setup**: Configure different types of DMX fixtures (RGB, RGBW, Moving Heads, etc.)
- **Scene Designer**: Create and save lighting scenes with selective fixture control
- **Visual DMX Mapping**: See which DMX channels are assigned to which fixtures
- **Fixture Selection**: Choose which fixtures participate in each scene

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
- Click "Save Fixture"
- Repeat for all your fixtures

### 3. Scene Creation

Create lighting scenes:
- Go to "Setup" -> "Scene Setup"
- Click "Create New Scene"
- Enter a scene name
- Enable or disable fixtures you want to include in this scene
- Adjust the sliders for each enabled fixture's channels
- Click "Test Scene" to preview
- Click "Save Scene" when finished

### 4. Scene Control

Finally, use the main interface to activate your scenes:
- Go to "Scenes" page
- Click on any scene to activate it
- Only enabled fixtures in that scene will respond

## System Requirements

- Python 3.7+
- Network connection to DMX fixtures via Art-Net
- Modern web browser

## Technical Details

- Built with Flask (Python web framework)
- Uses StupidArtnet library for Art-Net protocol
- Responsive design works on desktop and mobile devices

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, feature requests, or contributions, please open an issue on GitHub or contact the project maintainer.
