"""
Scene Manager - Handles scene logic and DMX buffer building
"""
from flask import current_app


# Groups where only one member may be active at a time. Any group not in
# this set (e.g. 'extra', or no group at all) is an independent toggle that
# layers on top of whatever else is active without excluding anything.
EXCLUSIVE_GROUPS = {'main', 'achtergrond', 'sfeer', 'aanuit'}


class SceneManager:
    """Manages lighting scenes and DMX buffer construction"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.active_layers = {}  # scene_name -> True, insertion-ordered (oldest first)
        self.highest_active_idx = 0
        self.scenes = {}  # Cache of scene name -> full scene dict

    def load_scenes(self):
        """Load scenes from configuration"""
        try:
            scenes_list = self.config_manager.get_scenes()
            self.scenes = {scene['name']: scene for scene in scenes_list}
            # Drop any active layers referring to scenes that no longer exist
            self.active_layers = {
                name: True for name in self.active_layers if name in self.scenes
            }
            return True
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error loading scenes: {e}")
            return False

    def get_available_scenes(self):
        """Get list of available scene names"""
        return list(self.scenes.keys())

    def get_active_scenes(self):
        """Get the list of currently active scene names, oldest layer first"""
        return list(self.active_layers.keys())

    def get_active_scene(self):
        """Backward-compatible single active scene (the most recently activated one)"""
        layers = self.get_active_scenes()
        return layers[-1] if layers else None

    def get_highest_active_idx(self):
        """Get the highest active DMX channel index"""
        return self.highest_active_idx

    def _apply_scene(self, buffer, scene):
        """
        Apply one scene's channel values onto an existing buffer (in place).

        A scene's channel map holds exactly the channels it claims, so
        presence is the whole rule: write every entry, including a stored
        zero, and leave every absent channel to whatever other layers put
        there. This used to be two rules branching on `enabledFixtures`,
        which existed only because a full-length array could not tell a
        deliberate zero apart from an unclaimed channel.
        """
        for channel, value in scene['channels'].items():
            index = channel - 1  # map keys are 1-based DMX channel numbers
            if 0 <= index < 512:
                buffer[index] = value
                self.highest_active_idx = max(self.highest_active_idx, index)

    def _rebuild_buffer(self):
        """Recompute the full 512-channel buffer from all currently active layers"""
        buffer = bytearray(512)
        self.highest_active_idx = 0
        for name in self.active_layers:
            scene = self.scenes.get(name)
            if scene:
                self._apply_scene(buffer, scene)
        return buffer

    def toggle_scene(self, scene_name):
        """
        Toggle a scene on or off and rebuild the DMX buffer from all
        currently active layers.

        - Clicking an already-active scene turns it off; any channels it
          defined fall back to whatever remaining active layers define, or 0.
        - Clicking an inactive scene in an exclusive group (main/achtergrond/
          sfeer/aanuit) replaces that group's currently active member.
        - Clicking an inactive scene in a non-exclusive group (e.g. 'extra')
          just adds it on top of whatever else is active.

        Returns: (buffer, success, active_scene_names)
        """
        if scene_name not in self.scenes:
            if current_app:
                current_app.logger.error(f"Scene '{scene_name}' not found")
            return None, False, self.get_active_scenes()

        try:
            if scene_name in self.active_layers:
                del self.active_layers[scene_name]
            else:
                group = self.scenes[scene_name].get('group')
                if group in EXCLUSIVE_GROUPS:
                    for other in list(self.active_layers):
                        if self.scenes.get(other, {}).get('group') == group:
                            del self.active_layers[other]
                self.active_layers[scene_name] = True

            buffer = self._rebuild_buffer()

            if current_app:
                current_app.logger.info(f"Active layers now: {list(self.active_layers.keys())}")

            return buffer, True, self.get_active_scenes()

        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error toggling scene: {e}")
            return None, False, self.get_active_scenes()

    def save_scene(self, name, channels, group=None):
        """Save a scene (delegates to config manager)"""
        success = self.config_manager.save_scene(name, channels, group)
        if success:
            self.scenes[name] = {
                'name': name,
                'channels': channels,
                'group': group,
            }
        return success

    def delete_scene(self, name):
        """Delete a scene (delegates to config manager)"""
        success = self.config_manager.delete_scene(name)
        if success:
            self.scenes.pop(name, None)
            self.active_layers.pop(name, None)
        return success
