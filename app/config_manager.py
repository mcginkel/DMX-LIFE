"""
Config Manager - Handles all configuration file I/O operations
"""
import json
import os
from flask import current_app


class ConfigManager:
    """Manages reading and writing to the configuration JSON file"""
    
    def __init__(self, config_file):
        self.config_file = config_file
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Create default configuration file if it doesn't exist"""
        if not os.path.exists(self.config_file):
            default_config = {
                'artnet_ip': '255.255.255.255',  # Broadcast by default
                'artnet_port': 6454,
                'universe': 0,
                'packet_size': 512,
                'refresh_rate': 30,  # FPS
                'fixtures': [],
                'scenes': []
            }
            self.write(default_config)
    
    def read(self):
        """Read the entire configuration file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error reading configuration: {e}")
            raise
    
    def write(self, config):
        """Write the entire configuration file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error writing configuration: {e}")
            raise
    
    def update(self, **kwargs):
        """Update specific configuration keys"""
        try:
            config = self.read()
            config.update(kwargs)
            self.write(config)
            return config
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error updating configuration: {e}")
            return None
    
    def get_network_settings(self):
        """Get network-related settings"""
        config = self.read()
        return {
            'artnet_ip': config.get('artnet_ip', '255.255.255.255'),
            'artnet_port': config.get('artnet_port', 6454),
            'universe': config.get('universe', 0),
            'packet_size': config.get('packet_size', 512),
            'refresh_rate': config.get('refresh_rate', 30)
        }
    
    def update_network_settings(self, artnet_ip=None, artnet_port=None, 
                               universe=None, refresh_rate=None):
        """Update network settings"""
        updates = {}
        if artnet_ip is not None:
            updates['artnet_ip'] = artnet_ip
        if artnet_port is not None:
            updates['artnet_port'] = artnet_port
        if universe is not None:
            updates['universe'] = universe
        if refresh_rate is not None:
            updates['refresh_rate'] = refresh_rate
        
        return self.update(**updates)
    
    def get_fixtures(self):
        """Get all fixtures"""
        config = self.read()
        return config.get('fixtures', [])
    
    def save_fixtures(self, fixtures):
        """Save fixtures list"""
        return self.update(fixtures=fixtures)
    
    def get_scenes(self):
        """Get all scenes"""
        config = self.read()
        return config.get('scenes', [])
    
    def save_scene(self, name, channels, enabled_fixtures=None):
        """Save or update a scene"""
        try:
            config = self.read()
            scenes = config.get('scenes', [])
            
            # Check if scene exists
            scene_index = None
            for i, scene in enumerate(scenes):
                if scene['name'] == name:
                    scene_index = i
                    break
            
            # Create scene data
            scene_data = {
                'name': name,
                'channels': channels,
                'enabledFixtures': enabled_fixtures if enabled_fixtures is not None else []
            }
            
            # Update or append
            if scene_index is not None:
                scenes[scene_index] = scene_data
            else:
                scenes.append(scene_data)
            
            # Save back
            config['scenes'] = scenes
            self.write(config)
            return True
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error saving scene: {e}")
            return False
    
    def delete_scene(self, name):
        """Delete a scene by name"""
        try:
            config = self.read()
            scenes = config.get('scenes', [])
            
            # Filter out the scene to delete
            scenes = [scene for scene in scenes if scene['name'] != name]
            
            config['scenes'] = scenes
            self.write(config)
            return True
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error deleting scene: {e}")
            return False
    
    def get_scene_by_name(self, name):
        """Get a specific scene by name"""
        scenes = self.get_scenes()
        for scene in scenes:
            if scene['name'] == name:
                return scene
        return None
