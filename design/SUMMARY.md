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

3. **Flexible Fixture Support**
   - Support for common fixture types (RGB, RGBW, Moving Heads, etc.)
   - Visual indication of DMX channel assignment
   - Detection of channel conflicts

## Technical Details

- **Flask Web Framework**: Powers the backend and web interface
- **StupidArtnet Library**: Provides Art-Net protocol communication
- **Responsive Design**: Works on desktops, tablets, and mobile devices
- **Configuration Storage**: Settings stored in JSON file for persistence

## Running the Application

1. Start the application: 
   ```
   python app.py
   ```

2. Access the web interface:
   ```
   http://localhost:5050
   ```

3. Setup Workflow:
   - First, configure network settings
   - Next, add your DMX fixtures
   - Finally, create lighting scenes
   - Return to the main page to activate scenes

## Future Improvements

- DMX input support for remote control
- Scene transition effects
- Timeline-based scene sequencing
- Support for multiple DMX universes
- User authentication and multi-user support
