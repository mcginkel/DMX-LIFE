"""
Scene Manager - Handles scene logic and DMX buffer building
"""
from flask import current_app


class SceneManager:
    """Manages lighting scenes and DMX buffer construction"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.active_scene = None
        self.highest_active_idx = 0
        self.scenes = {}  # Cache of scene names to channel data
    
    def load_scenes(self):
        """Load scenes from configuration"""
        try:
            scenes_list = self.config_manager.get_scenes()
            self.scenes = {scene['name']: scene['channels'] for scene in scenes_list}
            return True
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error loading scenes: {e}")
            return False
    
    def get_available_scenes(self):
        """Get list of available scene names"""
        return list(self.scenes.keys())
    
    def get_active_scene(self):
        """Get the currently active scene name"""
        return self.active_scene
    
    def get_highest_active_idx(self):
        """Get the highest active DMX channel index"""
        return self.highest_active_idx
    
    def build_dmx_buffer(self, scene_name, current_values=None):
        """
        Build a DMX buffer for the specified scene.
        
        Args:
            scene_name: Name of the scene to build
            current_values: Current DMX values (bytearray) to preserve for disabled fixtures
            
        Returns:
            tuple: (buffer as bytearray(512), success as bool)
        """
        if scene_name not in self.scenes:
            if current_app:
                current_app.logger.error(f"Scene '{scene_name}' not found")
            return None, False
        
        try:
            # Get the full scene configuration
            scene_config = self.config_manager.get_scene_by_name(scene_name)
            if not scene_config:
                if current_app:
                    current_app.logger.error(f"Scene '{scene_name}' not found in config")
                return None, False
            
            channel_values = scene_config['channels']
            enabled_fixtures = scene_config.get('enabledFixtures', [])
            
            # Get fixtures for selective application
            fixtures = self.config_manager.get_fixtures()
            
            # Create buffer, starting with current values if provided
            buffer = bytearray(512)
            if current_values:
                for i in range(512):
                    buffer[i] = current_values[i]
            
            # Reset highest active index
            self.highest_active_idx = 0
            
            # If no specific fixture is enabled, activate all channels
            if not enabled_fixtures:
                for channel, value in enumerate(channel_values):
                    if 0 <= channel < 512 and value:
                        buffer[channel] = value
                self.highest_active_idx = 511
            else:
                # Apply channel values only for enabled fixtures
                for fixture in fixtures:
                    fixture_name = fixture.get('name', '')
                    
                    # Skip if fixture is not enabled in this scene
                    if fixture_name not in enabled_fixtures:
                        continue
                    
                    # Apply channel values for this fixture
                    start_channel = fixture.get('start_channel', 1) - 1  # Convert to 0-based
                    channel_count = fixture.get('channel_count', 1)
                    
                    self.highest_active_idx = max(
                        self.highest_active_idx, 
                        start_channel + channel_count - 1
                    )
                    
                    for i in range(channel_count):
                        channel = start_channel + i
                        if 0 <= channel < 512 and channel < len(channel_values):
                            buffer[channel] = channel_values[channel]
            
            # Update active scene
            self.active_scene = scene_name
            
            if current_app:
                current_app.logger.info(f"Scene '{scene_name}' prepared for activation")
            
            return buffer, True
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error building DMX buffer: {e}")
            return None, False
    
    def save_scene(self, name, channels, enabled_fixtures=None):
        """Save a scene (delegates to config manager)"""
        success = self.config_manager.save_scene(name, channels, enabled_fixtures)
        if success:
            # Update cache
            self.scenes[name] = channels
        return success
    
    def delete_scene(self, name):
        """Delete a scene (delegates to config manager)"""
        success = self.config_manager.delete_scene(name)
        if success and name in self.scenes:
            # Update cache
            del self.scenes[name]
            # Clear active scene if it was deleted
            if self.active_scene == name:
                self.active_scene = None
        return success
