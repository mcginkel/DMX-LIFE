"""
Config Manager - Handles all configuration file I/O operations
"""
import copy
import datetime
import json
import os
import shutil
from flask import current_app

from app.dmx_backends.factory import BACKEND_ARTNET, DEFAULT_OUTPUT

# Top-level keys that predate the `output` section, moved into output.artnet
# on read. `refresh_rate` is deliberately not among them - its fate is a
# separate open question (see the change's task 8.1), so it stays put.
LEGACY_OUTPUT_KEYS = ('artnet_ip', 'artnet_port', 'universe', 'packet_size')


class ConfigManager:
    """Manages reading and writing to the configuration JSON file"""
    
    def __init__(self, config_file):
        self.config_file = config_file
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Create default configuration file if it doesn't exist"""
        if not os.path.exists(self.config_file):
            default_config = {
                'output': copy.deepcopy(DEFAULT_OUTPUT),
                'refresh_rate': 30,  # FPS
                'fixtures': [],
                'scenes': []
            }
            self.write(default_config)
    
    def read(self):
        """Read the entire configuration file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self._migrate_output_settings(config)
            self._migrate_fixture_links(config.get('fixtures', []))
            self._migrate_scene_channels(
                config.get('scenes', []), config.get('fixtures', [])
            )
            return config
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

    def _snapshot_daily_backup(self):
        """
        Copy the current on-disk config to backups/config-<date>.json if
        today doesn't have one yet.

        Best-effort: any failure here (permissions, disk full, ...) is
        logged and swallowed, never allowed to block the real write it
        guards. Runs before the atomic-write sequence, since it needs to
        capture the file exactly as it stood before this write touches it.
        """
        if not os.path.exists(self.config_file):
            return

        try:
            today = datetime.date.today().isoformat()
            backups_dir = os.path.join(os.path.dirname(self.config_file), '..', 'backups')
            snapshot_path = os.path.join(backups_dir, f"config-{today}.json")

            if os.path.exists(snapshot_path):
                return

            os.makedirs(backups_dir, exist_ok=True)
            shutil.copy2(self.config_file, snapshot_path)
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error creating daily config snapshot: {e}")

    def write(self, config):
        """
        Write the entire configuration file atomically.

        Serialises to a temporary file in the same directory, fsyncs it so
        the content is durable, moves any existing file aside as a backup,
        then atomically replaces the target with the new content. A reader
        never observes a partial or empty file: at every point it is either
        the complete previous version or the complete new one.
        """
        self._snapshot_daily_backup()

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

    def _migrate_output_settings(self, config):
        """
        Move legacy top-level Art-Net keys into an `output` section, in place.

        Output used to be Art-Net and nothing else, so its settings sat at the
        top level of the config. With a backend to choose, those settings
        become one backend's settings among others and move under
        `output.artnet`, with `output.backend` recording the choice.

        A config already carrying an `output` section is left exactly as it
        is, so this is safe on every read. Both backends' settings sub-objects
        are present from the start, so choosing a different backend in the UI
        does not discard the settings of the one being switched away from.
        """
        if isinstance(config.get('output'), dict):
            return  # already migrated

        legacy = {key: config[key] for key in LEGACY_OUTPUT_KEYS if key in config}
        defaults = DEFAULT_OUTPUT['artnet']

        if not legacy:
            # Neither shape present (an unusually sparse config): fall back to
            # defaults rather than leaving no output configuration at all.
            config['output'] = copy.deepcopy(DEFAULT_OUTPUT)
            return

        config['output'] = {
            'backend': BACKEND_ARTNET,
            'artnet': {
                'ip': config.pop('artnet_ip', defaults['ip']),
                'port': config.pop('artnet_port', defaults['port']),
                'universe': config.pop('universe', defaults['universe']),
                'packet_size': config.pop('packet_size', defaults['packet_size']),
            },
            'enttec_usb': copy.deepcopy(DEFAULT_OUTPUT['enttec_usb']),
        }

        if current_app:
            moved = ', '.join(f"{k}={v!r}" for k, v in legacy.items())
            current_app.logger.warning(
                "Migrated Art-Net settings into the output section:\n"
                f"  before (top level): {moved}\n"
                f"  after  (output.artnet): {config['output']['artnet']}\n"
                f"  output.backend: {BACKEND_ARTNET}"
            )

    def _migrate_scene_channels(self, scenes, fixtures):
        """
        Convert legacy 512-entry `channels` arrays to a sparse
        `{channel: value}` map, in place. A config already using maps is left
        as-is apart from key normalisation - safe to call on every read.

        The old array format could not distinguish "channel deliberately set
        to zero" from "channel this scene has no opinion about", so which
        channels a scene claimed had to be carried separately in
        `enabledFixtures`, with two different meanings (ADR-0007):

        - non-empty: copy each named fixture's *entire* channel range,
          zeros included;
        - empty: a sparse overlay of only the non-zero values.

        Both collapse into presence-as-the-signal here: the migrated map
        holds exactly the channels that scene claimed under whichever rule
        applied to it, so `enabledFixtures` carries no information the map
        does not and is dropped.

        This is also the single boundary where JSON's string keys become
        ints. Everything downstream works with a genuine int -> int map, so
        a string channel number can never be compared against an int one.
        """
        conversions = []

        for scene in scenes:
            channels = scene.get('channels')

            if isinstance(channels, dict):
                # Already migrated. Only normalise the keys JSON gave us as
                # strings; entries that cannot be a channel number are
                # dropped rather than left to fail an int comparison later.
                normalised = {}
                for key, value in channels.items():
                    try:
                        normalised[int(key)] = value
                    except (TypeError, ValueError):
                        continue
                scene['channels'] = normalised
                scene.pop('enabledFixtures', None)
                continue

            if not isinstance(channels, list):
                continue

            enabled_fixtures = scene.get('enabledFixtures') or []
            migrated = {}

            if enabled_fixtures:
                for fixture in fixtures:
                    if fixture.get('name', '') not in enabled_fixtures:
                        continue
                    start_channel = fixture.get('start_channel', 1)
                    channel_count = fixture.get('channel_count', 1)
                    for offset in range(channel_count):
                        channel = start_channel + offset  # 1-based
                        index = channel - 1
                        if 1 <= channel <= 512 and index < len(channels):
                            migrated[channel] = channels[index]
            else:
                for index, value in enumerate(channels):
                    if index < 512 and value:
                        migrated[index + 1] = value

            scene['channels'] = migrated
            scene.pop('enabledFixtures', None)
            conversions.append((scene.get('name'), len(channels), len(migrated)))

        if conversions and current_app:
            lines = ["Migrated scene channels from full arrays to sparse maps:"]
            for name, before, after in conversions:
                lines.append(f"  {name}: {before} stored channels -> {after}")
            current_app.logger.warning("\n".join(lines))

    def _migrate_fixture_links(self, fixtures):
        """
        Convert legacy positional `linked_to` indices to master fixture names,
        in place. A config already using names is left untouched — this is
        safe to call on every read.

        Positional indices are fragile (ADR-0010): reordering, inserting or
        deleting a fixture invalidates every link, and a shift that touches
        the data but not the links produces self-references or chains that
        the UI is supposed to make impossible but the stored data can still
        contain. Repair proceeds in three passes:

        1. Detect self-referential entries (`linked_to == own index`) and
           compute their corrected target as `index - 1`, if that fixture
           exists and is of the same type. This is the specific off-by-one
           shape the known bad data takes.
        2. Resolve every other integer `linked_to`. A raw value pointing at
           a *self-referential* index is flattened straight to that entry's
           corrected target, rather than to the buggy fixture itself — this
           is what turns four fixtures that all raw-point at one broken
           self-reference into four fixtures pointing at the one real
           master, instead of a chain through the broken one.
        3. Reject any resolution whose target is itself linked to something
           else post-resolution: that is a chain, which the rest of this
           change forbids. The fixture is left unlinked with a warning
           rather than guessed at further.
        """
        self_correction = {}
        for i, fixture in enumerate(fixtures):
            if fixture.get('linked_to') == i:
                candidate_index = i - 1
                if (
                    0 <= candidate_index < len(fixtures)
                    and fixtures[candidate_index].get('type') == fixture.get('type')
                ):
                    self_correction[i] = candidate_index

        conversions = []
        resolved = {}  # fixture index -> resolved name or None, this pass only

        for i, fixture in enumerate(fixtures):
            linked_to = fixture.get('linked_to')
            if not isinstance(linked_to, int):
                continue  # already a name (or unlinked) - nothing to migrate

            if linked_to == i:
                target_index = self_correction.get(i)
            elif linked_to in self_correction:
                target_index = self_correction[linked_to]
            else:
                target_index = linked_to

            resolved_name = None
            if (
                target_index is not None
                and 0 <= target_index < len(fixtures)
                and target_index != i
                and fixtures[target_index].get('type') == fixture.get('type')
            ):
                resolved_name = fixtures[target_index]['name']

            resolved[i] = resolved_name
            conversions.append([fixture.get('name'), linked_to, resolved_name])

        # Reject chains: a resolved target that is itself linked (to
        # anything, old-style index or already-migrated name) can't be used.
        for i, resolved_name in resolved.items():
            if resolved_name is None:
                continue
            target = next((f for f in fixtures if f.get('name') == resolved_name), None)
            if target is None:
                continue
            target_index = fixtures.index(target)
            target_is_linked = (
                target.get('linked_to') is not None
                if target_index not in resolved
                else resolved.get(target_index) is not None
            )
            if target_is_linked:
                for row in conversions:
                    if row[0] == fixtures[i]['name']:
                        row[2] = None
                resolved[i] = None

        for i, resolved_name in resolved.items():
            fixtures[i]['linked_to'] = resolved_name

        if conversions and current_app:
            lines = ["Migrated fixture links from positional indices to names:"]
            for name, original_index, new_value in conversions:
                outcome = f"'{new_value}'" if new_value else "unlinked (could not be resolved safely)"
                lines.append(f"  {name}: index {original_index} -> {outcome}")
            current_app.logger.warning("\n".join(lines))

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
    
    def get_output_settings(self):
        """The whole output section: which backend is active and every
        backend's own settings."""
        return self.read().get('output', copy.deepcopy(DEFAULT_OUTPUT))

    def get_network_settings(self):
        """
        Art-Net settings in the flat shape the Network Setup page uses.

        Kept flat for the UI's benefit; the stored shape is nested under
        `output.artnet`.
        """
        config = self.read()
        output = config.get('output', {})
        artnet = output.get('artnet', {})
        defaults = DEFAULT_OUTPUT['artnet']
        return {
            'backend': output.get('backend', BACKEND_ARTNET),
            'artnet_ip': artnet.get('ip', defaults['ip']),
            'artnet_port': artnet.get('port', defaults['port']),
            'universe': artnet.get('universe', defaults['universe']),
            'packet_size': artnet.get('packet_size', defaults['packet_size']),
            'enttec_port': (output.get('enttec_usb') or {}).get('port', ''),
            'refresh_rate': config.get('refresh_rate', 30)
        }
    
    def update_network_settings(self, artnet_ip=None, artnet_port=None,
                               universe=None, refresh_rate=None):
        """Update the Art-Net backend's settings, written to output.artnet."""
        config = self.read()
        output = config.get('output', copy.deepcopy(DEFAULT_OUTPUT))
        artnet = output.setdefault('artnet', copy.deepcopy(DEFAULT_OUTPUT['artnet']))

        for key, value in (('ip', artnet_ip), ('port', artnet_port),
                           ('universe', universe)):
            if value is not None:
                artnet[key] = value

        updates = {'output': output}
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
    
    def save_scene(self, name, channels, group=None):
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
