"""
Setup views for DMX configuration
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app import auth
from app.views.main import GROUP_ORDER
from app.dmx_backends.factory import (
    BACKEND_ARTNET, BACKEND_ENTTEC_USB, DEFAULT_OUTPUT, SUPPORTED_BACKENDS,
)
from app.dmx_controller import get_config, save_config, save_scene, delete_scene, test_scene
from app.models.fixture import FixtureType

setup_bp = Blueprint('setup', __name__)

# Request validation helpers


def get_json_object():
    """Return the request body as a dict, or None if absent or not an object"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    return data


# The groups a scene can be assigned to in the editor. GROUP_ORDER is the
# exclusive groups in main-page display order; 'extra' layers independently
# on top of them, so it is not part of that ordering but is still selectable.
SCENE_GROUP_CHOICES = GROUP_ORDER + [('extra', 'Extra')]


def parse_channel_map(channels):
    """
    Validate a scene's channel map and normalise its keys to ints.

    Accepts a mapping of channel number (1-512) to value (0-255). JSON
    object keys always arrive as strings, so this is the boundary where they
    become ints - everything downstream compares int channel numbers and
    must never meet a string one.

    Returns (channel_map, None) when valid, otherwise (None, message).
    Booleans are rejected explicitly, for keys and values alike, because
    bool is a subclass of int in Python.
    """
    if not isinstance(channels, dict):
        return None, 'Channels must be an object mapping channel number to value'

    parsed = {}
    for key, value in channels.items():
        if isinstance(key, bool) or not isinstance(key, (str, int)):
            return None, f'Channel number {key!r} is not an integer'
        try:
            channel = int(key)
        except ValueError:
            return None, f'Channel number {key!r} is not an integer'

        if not 1 <= channel <= 512:
            return None, f'Channel number {channel} is out of range (1-512)'
        if isinstance(value, bool) or not isinstance(value, int):
            return None, f'Channel {channel} is not an integer'
        if not 0 <= value <= 255:
            return None, f'Channel {channel} is out of range (0-255)'

        parsed[channel] = value

    return parsed, None


def find_invalid_fixtures(fixtures):
    """
    Validate a fixture list before it is saved.

    Names must be unique, since a link identifies its master by name. Any
    link must name a different, existing fixture of the same type that is
    not itself linked to something else - the last of these is what prevents
    chains, which the editor's own rules also forbid but only in the browser.

    Returns None if valid, otherwise a message naming the problem.
    """
    if not isinstance(fixtures, list):
        return 'Fixtures must be a list'

    seen_names = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict) or not fixture.get('name'):
            return 'Each fixture must have a name'
        name = fixture['name']
        if name in seen_names:
            return f"Duplicate fixture name: '{name}'"
        seen_names.add(name)

    by_name = {fixture['name']: fixture for fixture in fixtures}

    for fixture in fixtures:
        linked_to = fixture.get('linked_to')
        if linked_to is None:
            continue

        name = fixture['name']
        if not isinstance(linked_to, str):
            return f"'{name}' has an invalid link (expected a fixture name)"
        if linked_to == name:
            return f"'{name}' cannot be linked to itself"

        master = by_name.get(linked_to)
        if master is None:
            return f"'{name}' is linked to unknown fixture '{linked_to}'"
        if master.get('type') != fixture.get('type'):
            return f"'{name}' cannot be linked to '{linked_to}' (different fixture type)"
        if master.get('linked_to') is not None:
            return f"'{name}' cannot be linked to '{linked_to}' because it is itself linked"

    return None


@setup_bp.route('/')
@auth.login_required
def index():
    """Setup main page"""
    return render_template('setup/index.html')

@setup_bp.route('/network')
@auth.login_required
def network():
    """Output backend and its connection settings"""
    config = get_config()
    output = config.get('output') or DEFAULT_OUTPUT
    return render_template(
        'setup/network.html',
        config=config,
        output=output,
        backends=sorted(SUPPORTED_BACKENDS.items()),
    )

@setup_bp.route('/fixtures')
@auth.login_required
def fixtures():
    """DMX fixture configuration"""
    config = get_config()
    fixture_types = FixtureType.get_types()
    return render_template('setup/fixtures.html', 
                          config=config, 
                          fixture_types=fixture_types)

@setup_bp.route('/scenes')
@auth.login_required
def scenes():
    """Scene editor"""
    config = get_config()
    return render_template('setup/scenes.html', config=config,
                           group_choices=SCENE_GROUP_CHOICES)

# API endpoints for setup

@setup_bp.route('/api/config', methods=['GET'])
@auth.login_required
def get_config_endpoint():
    """Get current configuration, plus the scene limit the editor enforces"""
    config = dict(get_config())
    config['MAX_SCENES'] = current_app.config['MAX_SCENES']
    return jsonify(config)

def _parse_bounded_int(raw, label, minimum, maximum):
    """Returns (value, None) or (None, message)."""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None, f'{label} must be a number'
    if not minimum <= value <= maximum:
        return None, f'{label} must be between {minimum} and {maximum}'
    return value, None


@setup_bp.route('/api/config/network', methods=['POST'])
@auth.login_required
def update_network_config():
    """
    Update the output backend selection and the backends' settings.

    Each backend's settings are validated on their own terms - Art-Net's are
    numeric, the USB backend's is a device path - and only the backend being
    made active has to be fully configured. Settings for the other backend
    are still stored, so switching away and back does not lose them.

    Nothing is saved unless everything validates, so a bad value cannot leave
    the configuration half-updated.
    """
    data = get_json_object()
    if data is None:
        return jsonify({'success': False, 'message': 'JSON body required'}), 400

    backend = data.get('backend', BACKEND_ARTNET)
    if backend not in SUPPORTED_BACKENDS:
        known = ', '.join(sorted(SUPPORTED_BACKENDS))
        return jsonify({
            'success': False,
            'message': f"Unknown output backend '{backend}'. Choose one of: {known}"
        }), 400

    # Start from what is stored so an unsupplied field keeps its value.
    stored_output = (get_config() or {}).get('output') or {}
    artnet = dict(DEFAULT_OUTPUT['artnet'], **(stored_output.get('artnet') or {}))
    enttec = dict(DEFAULT_OUTPUT['enttec_usb'], **(stored_output.get('enttec_usb') or {}))

    # -- Art-Net settings ------------------------------------------------
    supplied_artnet = data.get('artnet') or {}
    if 'ip' in supplied_artnet or backend == BACKEND_ARTNET:
        ip = supplied_artnet.get('ip', artnet['ip'])
        if not isinstance(ip, str) or not ip.strip():
            return jsonify({'success': False, 'message': 'Art-Net IP address is required'}), 400
        artnet['ip'] = ip.strip()

    for key, label, low, high in (('port', 'Art-Net port', 1, 65535),
                                  ('universe', 'Universe', 0, 32767)):
        if key in supplied_artnet:
            value, error = _parse_bounded_int(supplied_artnet[key], label, low, high)
            if error:
                return jsonify({'success': False, 'message': error}), 400
            artnet[key] = value

    # -- Enttec USB settings ---------------------------------------------
    supplied_enttec = data.get('enttec_usb') or {}
    if 'port' in supplied_enttec:
        device = supplied_enttec['port']
        if not isinstance(device, str):
            return jsonify({'success': False, 'message': 'Serial port must be text'}), 400
        enttec['port'] = device.strip()
    if backend == BACKEND_ENTTEC_USB and not enttec['port']:
        return jsonify({
            'success': False,
            'message': 'A serial port is required to use the Enttec DMX USB Pro'
        }), 400

    updates = {'output': {'backend': backend, 'artnet': artnet, 'enttec_usb': enttec}}

    if 'refresh_rate' in data:
        value, error = _parse_bounded_int(data['refresh_rate'], 'refresh_rate', 1, 60)
        if error:
            return jsonify({'success': False, 'message': error}), 400
        updates['refresh_rate'] = value

    if save_config(updates):
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Failed to save network settings'}), 500

@setup_bp.route('/api/config/fixtures', methods=['POST'])
@auth.login_required
def update_fixtures():
    """Update fixture configuration"""
    data = get_json_object()
    if data is None:
        return jsonify({'success': False, 'message': 'JSON body required'}), 400

    if 'fixtures' not in data:
        return jsonify({'success': False, 'message': 'No fixtures provided'}), 400

    invalid = find_invalid_fixtures(data['fixtures'])
    if invalid:
        return jsonify({'success': False, 'message': invalid}), 400

    success = save_config({'fixtures': data['fixtures']})
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Failed to save fixtures'}), 500

@setup_bp.route('/api/config/scenes', methods=['POST'])
@auth.login_required
def save_scene_endpoint():
    """Create or update a scene"""
    data = get_json_object()
    if data is None:
        return jsonify({'success': False, 'message': 'JSON body required'}), 400

    if not data.get('name') or 'channels' not in data:
        return jsonify({'success': False, 'message': 'Scene name and channels required'}), 400

    channel_map, invalid = parse_channel_map(data['channels'])
    if invalid:
        return jsonify({'success': False, 'message': invalid}), 400

    group = data.get('group', None)

    success = save_scene(data['name'], channel_map, group)
    if success:
        return jsonify({'success': True})
    
    # If we have max scenes, return appropriate error
    if len(get_config().get('scenes', [])) >= current_app.config['MAX_SCENES']:
        return jsonify({
            'success': False, 
            'message': f"Maximum {current_app.config['MAX_SCENES']} scenes allowed"
        }), 400
    
    return jsonify({'success': False, 'message': 'Failed to save scene'}), 500

@setup_bp.route('/api/config/scenes', methods=['DELETE'])
@auth.login_required
def delete_scene_endpoint():
    """ Delete a scene"""
    data = get_json_object()
    if data is None:
        return jsonify({'success': False, 'message': 'JSON body required'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'message': 'Scene name required'}), 400

    success = delete_scene(name)
    if success:
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Failed to delete scene'}), 500


@setup_bp.route('/api/config/scenes/test', methods=['POST'])
@auth.login_required
def test_scene_endpoint():
    """test a scene"""
    data = get_json_object()
    if data is None:
        return jsonify({'success': False, 'message': 'JSON body required'}), 400

    if 'channels' not in data:
        return jsonify({'success': False, 'message': 'Channels required'}), 400

    channel_map, invalid = parse_channel_map(data['channels'])
    if invalid:
        return jsonify({'success': False, 'message': invalid}), 400

    success = test_scene(channel_map)
    if success:
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Failed to test scene'}), 500

@setup_bp.route('/api/fixture-types')
@auth.login_required
def get_fixture_types():
    """Get available fixture types"""
    return jsonify({
        'types': FixtureType.get_types()
    })

@setup_bp.route('/api/fixture-types/<fixture_type>')
@auth.login_required
def get_fixture_type_details(fixture_type):
    """Get channel details for a fixture type"""
    channels = FixtureType.get_channels(fixture_type)
    return jsonify({
        'type': fixture_type,
        'channels': channels
    })
