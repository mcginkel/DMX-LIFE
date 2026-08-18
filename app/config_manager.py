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
        except json.JSONDecodeError as e:
            backup_path = f"{self.config_file}.bak"
            message = f"Configuration file '{self.config_file}' is not valid JSON: {e}."
            if os.path.exists(backup_path):
                message += (
                    f" A previous version is available at '{backup_path}' and can be "
                    f"restored by copying it over '{self.config_file}'."
                )
            else:
                message += " No backup is available to restore from."
            if current_app:
                current_app.logger.error(message)
            raise RuntimeError(message) from e
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error reading configuration: {e}")
            raise

    def write(self, config):
        """
        Write the entire configuration file atomically.

        Serialises to a temporary file in the same directory, fsyncs it so
        the content is durable, moves any existing file aside as a backup,
        then atomically replaces the target with the new content. A reader
        never observes a partial or empty file: at every point it is either
        the complete previous version or the complete new one.
        """
        tmp_path = f"{self.config_file}.tmp"
        backup_path = f"{self.config_file}.bak"
        had_previous = os.path.exists(self.config_file)

        try:
            with open(tmp_path, 'w') as f:
                json.dump(config, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            if had_previous:
                os.replace(self.config_file, backup_path)

            try:
                os.replace(tmp_path, self.config_file)
            except Exception:
                # The rename that makes the new content visible failed after
                # the previous version was already moved aside. Put it back
                # so the target is never left missing.
                if had_previous:
                    os.replace(backup_path, self.config_file)
                raise

        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
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
    
    def save_scene(self, name, channels, enabled_fixtures=None, group=None):
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
                'enabledFixtures': enabled_fixtures if enabled_fixtures is not None else [],
                'group': group
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
