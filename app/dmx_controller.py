"""
DMX Life Integration Layer - Provides backward-compatible API
"""
from flask import current_app
from app.config_manager import ConfigManager
from app.scene_manager import SceneManager
from app.dmx_controller_class import DMXController

# Global instances
config_manager = None
scene_manager = None
dmx_controller = None

# Connection status tracking (for monitoring)
connection_status = {
    'connected': True,
    'last_error_time': 0,
    'error_message': None
}

# Fallback buffer returned only before the controller is initialized.
current_dmx_values = bytearray(512)  # Default empty buffer


def get_current_dmx_values():
    """Get current DMX values as a point-in-time snapshot"""
    if not dmx_controller:
        return current_dmx_values
    return dmx_controller.get_current_values()


def init_dmx_controller(app):
    """Initialize the DMX controller system with application context"""
    global config_manager, scene_manager, dmx_controller

    # Initialize managers
    config_manager = ConfigManager(app.config['CONFIG_FILE'])
    scene_manager = SceneManager(config_manager)

    # Load scenes
    scene_manager.load_scenes()

    # Get network settings
    network_settings = config_manager.get_network_settings()

    # Initialize DMX controller
    dmx_controller = DMXController(
        network_settings['artnet_ip'],
        network_settings['universe'],
        network_settings['packet_size'],
        network_settings['refresh_rate']
    )


    # Register application lifecycle hooks
    @app.before_request
    def before_request():
        if not hasattr(app, '_dmx_initialized'):
            dmx_controller.start()
            app._dmx_initialized = True
    
    @app.teardown_appcontext
    def teardown_dmx(exception=None):
        pass  # Keep DMX running


# Scene management functions (backward compatible API)

def activate_scene(scene_name):
    """Toggle a lighting scene on/off with smooth transition.

    The DMX buffer is fully rebuilt from all currently active scenes each
    time, so turning a scene off correctly reveals whatever other active
    scenes still define for its channels (or 0 if nothing else does).
    Returns (success, active_scene_names).
    """
    if not scene_manager or not dmx_controller:
        if current_app:
            current_app.logger.error("DMX system not initialized")
        return False, []

    buffer, success, active_scenes = scene_manager.toggle_scene(scene_name)

    if not success:
        return False, active_scenes

    # Activate with smooth transition
    dmx_controller.set_with_transition(buffer)
    return True, active_scenes


def test_scene(channels):
    """Test a scene immediately without transition"""
    if not dmx_controller:
        if current_app:
            current_app.logger.error("DMX controller not initialized")
        return False

    if not isinstance(channels, list):
        if current_app:
            current_app.logger.error("test_scene expects a list of channel values")
        return False

    # Convert channels list to buffer. Values are validated here as well as at
    # the API boundary so that a bad call cannot raise from the assignment
    # below; bool is excluded because it is a subclass of int.
    buffer = bytearray(512)
    for channel, value in enumerate(channels):
        if channel >= 512:
            break
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255:
            if current_app:
                current_app.logger.error(
                    f"test_scene rejected invalid value at channel {channel + 1}: {value!r}"
                )
            return False
        buffer[channel] = value

    # Set immediately
    dmx_controller.set_immediate(buffer)
    return True


def get_active_scene():
    """Get the most recently activated scene (backward compatible)"""
    if not scene_manager:
        return None
    return scene_manager.get_active_scene()


def get_active_scenes():
    """Get the list of all currently active scene names"""
    if not scene_manager:
        return []
    return scene_manager.get_active_scenes()


def get_highest_active_idx():
    """Get the highest active DMX channel index"""
    if not scene_manager:
        return 0
    return scene_manager.get_highest_active_idx()


def get_available_scenes():
    """Get list of available scenes"""
    if not scene_manager:
        return []
    return scene_manager.get_available_scenes()


def save_scene(name, channel_values, enabled_fixtures=None, group=None):
    """Save a new scene"""
    if not scene_manager:
        return False

    # Check scene limit
    if len(scene_manager.scenes) >= current_app.config['MAX_SCENES'] and name not in scene_manager.scenes:
        return False

    return scene_manager.save_scene(name, channel_values, enabled_fixtures, group)


def delete_scene(name):
    """Delete a scene"""
    if not scene_manager:
        return False
    return scene_manager.delete_scene(name)


# Configuration functions (backward compatible API)

def get_config():
    """Get the current configuration"""
    if not config_manager:
        return None
    return config_manager.read()


def save_config(config_data):
    """Save configuration settings"""
    if not config_manager:
        return False
    
    try:
        # Update configuration
        updated_config = config_manager.update(**config_data)
        if not updated_config:
            return False
        
        # If network settings changed, reconfigure DMX controller
        network_keys = {'artnet_ip', 'universe', 'packet_size', 'refresh_rate'}
        if network_keys & config_data.keys():
            network_settings = config_manager.get_network_settings()
            dmx_controller.reconfigure(
                artnet_ip=network_settings['artnet_ip'],
                universe=network_settings['universe'],
                packet_size=network_settings['packet_size'],
                refresh_rate=network_settings['refresh_rate']
            )
        
        # If scenes changed, reload
        if 'scenes' in config_data:
            scene_manager.load_scenes()
        
        return True
        
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error saving configuration: {e}")
        return False


def get_connection_status():
    """Get the current Art-Net connection status"""
    if not dmx_controller:
        return connection_status.copy()
    return dmx_controller.get_connection_status()


def load_configuration():
    """Reload configuration from file (for backward compatibility)"""
    if not config_manager or not scene_manager:
        return False
    
    try:
        scene_manager.load_scenes()
        
        # Reconfigure DMX controller
        network_settings = config_manager.get_network_settings()
        dmx_controller.reconfigure(
            artnet_ip=network_settings['artnet_ip'],
            universe=network_settings['universe'],
            packet_size=network_settings['packet_size'],
            refresh_rate=network_settings['refresh_rate']
        )
        
        return True
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error loading configuration: {e}")
        return False
