"""
DMX Controller - Handles communication with DMX fixtures via Art-Net
"""
import json
import os
import time
import threading
from flask import current_app
from stupidArtnet import StupidArtnet

# Global DMX controller instance
dmx_controller = None
dmx_thread = None
dmx_running = False
active_scene = None
highest_active_idx = 0  # Highest active DMX channel index
scenes = {}

# Variables for smooth transitions and monitoring
current_dmx_values = bytearray(512)  # Current DMX values - exported for monitoring
target_dmx_values = bytearray(512)   # Target DMX values
transition_active = False            # Whether a transition is in progress
transition_start_time = 0            # When the transition started
TRANSITION_DURATION = 3.0            # Transition duration in seconds

def init_dmx_controller(app):
    """Initialize the DMX controller with application context"""
    
    # Load default configuration
    default_config = {
        'artnet_ip': '255.255.255.255',  # Broadcast by default
        'artnet_port': 6454,
        'universe': 0,
        'packet_size': 512,
        'refresh_rate': 30,  # FPS
        'fixtures': [],
        'scenes': []
    }
    
    # Create default configuration file if it doesn't exist
    config_file = app.config['CONFIG_FILE']
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
    
    # Register functions to handle application lifecycle
    @app.before_request
    def before_request():
        if not hasattr(app, '_dmx_initialized'):
            load_configuration()
            start_dmx_thread()
            app._dmx_initialized = True
    
    @app.teardown_appcontext
    def teardown_dmx(exception=None):
        pass #stop_dmx_thread()

def load_configuration():
    """Load DMX configuration from file"""
    global dmx_controller, scenes
    
    try:
        with open(current_app.config['CONFIG_FILE'], 'r') as f:
            config = json.load(f)
        
        # Initialize the Art-Net controller
        dmx_controller = StupidArtnet(
            config.get('artnet_ip', '255.255.255.255'),
            config.get('universe', 0),
            config.get('packet_size', 512),
            config.get('refresh_rate', 30)
        )
        # TODO : do we need this?
        dmx_controller.set_simplified(False)
        dmx_controller.set_net(0)
        dmx_controller.set_subnet(0)
        
        # Load scenes
        scenes = {scene['name']: scene['channels'] for scene in config.get('scenes', [])}
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error loading DMX configuration: {e}")
        return False

def start_dmx_thread():
    """Start the DMX sending thread"""
    global dmx_thread, dmx_running
    
    if dmx_thread is not None:
        return
    
    dmx_running = True
    dmx_thread = threading.Thread(target=dmx_thread_function)
    dmx_thread.daemon = True
    dmx_thread.start()

def stop_dmx_thread():
    """Stop the DMX sending thread"""
    global dmx_thread, dmx_running
    
    if dmx_thread is None:
        return
    
    dmx_running = False
    if dmx_controller:
        dmx_controller.stop()
    
    dmx_thread.join(timeout=2.0)
    dmx_thread = None

def dmx_thread_function():
    """Function that runs in the DMX thread"""
    global dmx_running, dmx_controller, active_scene, transition_active
    global current_dmx_values, target_dmx_values, transition_start_time
    
    if dmx_controller is None:
        return
    
    dmx_controller.start()
    
    while dmx_running:
        time.sleep(0.033)  # ~30fps update rate
        
        # Handle smooth transitions if active
        if transition_active:
            # Calculate progress (0.0 to 1.0)
            elapsed = time.time() - transition_start_time
            progress = min(elapsed / TRANSITION_DURATION, 1.0)
            
            # Update all DMX channels with interpolated values
            for i in range(512):
                if current_dmx_values[i] != target_dmx_values[i]:
                    # Linear interpolation between current and target values
                    current_value = current_dmx_values[i]
                    target_value = target_dmx_values[i]
                    interpolated = int(current_value + (target_value - current_value) * progress)
                    current_dmx_values[i] = interpolated
            

            
            # Check if transition is complete
            if progress >= 1.0:
                transition_active = False
                for i in range(512):
                    current_dmx_values[i] = target_dmx_values[i]# Ensure final values match targets exactly
        
            # Apply updated values to DMX controller
            dmx_controller.set(current_dmx_values)
        
def activate_scene(scene_name):
    """Activate a lighting scene"""
    global active_scene, scenes, dmx_controller, highest_active_idx
    
    if scene_name not in scenes:
        current_app.logger.error(f"Scene '{scene_name}' not found")
        return False
    current_app.logger.info(f"Scene '{scene_name}' activated")
    if dmx_controller is None:
        current_app.logger.error("DMX controller not initialized")
        return False
    
    try:
        # Get the scene configuration
        with open(current_app.config['CONFIG_FILE'], 'r') as f:
            config = json.load(f)
        
        # Find the scene in the config
        scene_config = next((scene for scene in config.get('scenes', []) 
                            if scene['name'] == scene_name), None)
        
        if not scene_config:
            current_app.logger.error(f"Scene '{scene_name}' not found in config file")
            return False
            
        # Get DMX values and enabled fixtures
        channel_values = scenes[scene_name]
        enabled_fixtures = scene_config.get('enabledFixtures', [])
        
        # Get fixtures for selective application
        fixtures = config.get('fixtures', [])
        
        # Convert scene data to byte array for DMX
        buffer = bytearray(512)
        
        # First set all channels to 0
        for i in range(512):
            buffer[i] = 0
            
        highest_active_idx = 0
        # If no specific fixture is enabled, activate all channels
        if not enabled_fixtures:
            for channel, value in enumerate(channel_values):
                if 0 <= channel < 512 and value:
                    buffer[channel] = value
            highest_active_idx = 511
        else:
            # Apply channel values only for enabled fixtures
            for fixture in fixtures:
                fixture_name = fixture.get('name', '')
                
                # Skip if fixture is not enabled in this scene
                if fixture_name not in enabled_fixtures:
                    continue
                    
                # Apply channel values for this fixture
                start_channel = fixture.get('start_channel', 1) - 1  # Convert to 0-based index
                channel_count = fixture.get('channel_count', 1)
                
                highest_active_idx = max(highest_active_idx, start_channel + channel_count - 1)
                for i in range(channel_count):
                    channel = start_channel + i
                    if 0 <= channel < 512 and channel < len(channel_values) :#and channel_values[channel]:
                        buffer[channel] = channel_values[channel]
        
        # Set up smooth transition to new scene
        global transition_active, transition_start_time, target_dmx_values
        
        # Store target values
        target_dmx_values = buffer
        
        # Start transition
        transition_active = True
        transition_start_time = time.time()
        
        active_scene = scene_name
        return True
    except Exception as e:
        current_app.logger.error(f"Error activating scene: {e}")
        return False

def get_active_scene():
    """Get the currently active scene"""
    return active_scene

def get_highest_active_idx():
    """Get the highest active DMX channel index"""
    return highest_active_idx

def get_available_scenes():
    """Get list of available scenes"""
    return list(scenes.keys())

def save_scene(name, channel_values, enabled_fixtures=None):
    """Save a new scene"""
    global scenes
    
    if not name:
        return False
    
    if len(scenes) >= current_app.config['MAX_SCENES'] and name not in scenes:
        return False
    
    # Update the scene in memory
    scenes[name] = channel_values
    
    # Update config file
    try:
        with open(current_app.config['CONFIG_FILE'], 'r') as f:
            config = json.load(f)
        
        # Update or add scene
        scene_list = []
        scene_updated = False
        
        for scene in config.get('scenes', []):
            if scene['name'] == name:
                scene['channels'] = channel_values
                # Update enabled fixtures if provided
                if enabled_fixtures is not None:
                    scene['enabledFixtures'] = enabled_fixtures
                # If no enabled fixtures key exists in the scene, add it
                elif 'enabledFixtures' not in scene:
                    scene['enabledFixtures'] = []
                scene_updated = True
            scene_list.append(scene)
        
        if not scene_updated:
            scene_data = {
                'name': name,
                'channels': channel_values
            }
            # Add enabled fixtures if provided
            if enabled_fixtures is not None:
                scene_data['enabledFixtures'] = enabled_fixtures
            
            scene_list.append(scene_data)
        
        config['scenes'] = scene_list
        
        with open(current_app.config['CONFIG_FILE'], 'w') as f:
            json.dump(config, f, indent=4)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving scene: {e}")
        return False

def delete_scene(name):
    """Delete a scene"""
    global scenes
    
    if not name:
        return False
    
    if name not in scenes:
        return False
    
    # Update the scene
    scenes.pop(name)
    
    # Update config file
    try:
        with open(current_app.config['CONFIG_FILE'], 'r') as f:
            config = json.load(f)
        
        # Update or add scene
        scene_list = config.get('scenes', [])
        scene_list = [scene for scene in scene_list if scene['name'] != name]
  
        config['scenes'] = scene_list
        
        with open(current_app.config['CONFIG_FILE'], 'w') as f:
            json.dump(config, f, indent=4)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting scene: {e}")
        return False

def test_scene(channels):
    if dmx_controller is None:
        current_app.logger.error("DMX controller not initialized")
        return False
        
    # Convert scene data to byte array for DMX
    buffer = bytearray(512)
    for channel, value in enumerate(channels):
        if 0 <= channel < 512:
            buffer[channel] = value
    
    dmx_controller.set(buffer)

    return True

def save_config(config_data):
    """Save configuration settings"""
    try:
        # Read existing config
        with open(current_app.config['CONFIG_FILE'], 'r') as f:
            config = json.load(f)
        
        # Update with new settings
        for key, value in config_data.items():
            config[key] = value
        
        # Write back to file
        with open(current_app.config['CONFIG_FILE'], 'w') as f:
            json.dump(config, f, indent=4)
        
        # Reload configuration
        load_configuration()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving configuration: {e}")
        return False

def get_config():
    """Get the current configuration"""
    try:
        with open(current_app.config['CONFIG_FILE'], 'r') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f"Error reading configuration: {e}")
        return None
