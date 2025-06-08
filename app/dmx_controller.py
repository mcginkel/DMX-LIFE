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
scenes = {}

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
    global dmx_running, dmx_controller, active_scene
    
    if dmx_controller is None:
        return
    
    dmx_controller.start()
    
    while dmx_running:
        time.sleep(0.1)  # Small sleep to prevent CPU hogging
        
        # DMX controller handles sending automatically once started

def activate_scene(scene_name):
    """Activate a lighting scene"""
    global active_scene, scenes, dmx_controller
    
    if scene_name not in scenes:
        current_app.logger.error(f"Scene '{scene_name}' not found")
        return False
    current_app.logger.info(f"Scene '{scene_name}' activated")
    if dmx_controller is None:
        current_app.logger.error("DMX controller not initialized")
        return False
    
    try:
        # Set DMX values for the scene
        channel_values = scenes[scene_name]
        
        # Convert scene data to byte array for DMX
        buffer = bytearray(512)
        for channel, value in enumerate(channel_values):
            if 0 <= channel < 512:
                buffer[channel] = value
        
        dmx_controller.set(buffer)
        
        active_scene = scene_name
        return True
    except Exception as e:
        current_app.logger.error(f"Error activating scene: {e}")
        return False

def get_active_scene():
    """Get the currently active scene"""
    return active_scene

def get_available_scenes():
    """Get list of available scenes"""
    return list(scenes.keys())

def save_scene(name, channel_values):
    """Save a new scene"""
    global scenes
    
    if not name:
        return False
    
    if len(scenes) >= current_app.config['MAX_SCENES'] and name not in scenes:
        return False
    
    # Update the scene
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
                scene_updated = True
            scene_list.append(scene)
        
        if not scene_updated:
            scene_list.append({
                'name': name,
                'channels': channel_values
            })
        
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
