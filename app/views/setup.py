"""
Setup views for DMX configuration
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app import auth
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


def find_invalid_channel(channels):
    """
    Check that channels is a list of integers in 0-255.

    Returns None if valid, otherwise a message naming the problem. Booleans are
    rejected explicitly because bool is a subclass of int in Python.
    """
    if not isinstance(channels, list):
        return 'Channels must be a list'

    for index, value in enumerate(channels):
        if isinstance(value, bool) or not isinstance(value, int):
            return f'Channel {index + 1} is not an integer'
        if not 0 <= value <= 255:
            return f'Channel {index + 1} is out of range (0-255)'

    return None


@setup_bp.route('/')
@auth.login_required
def index():
    """Setup main page"""
    return render_template('setup/index.html')

@setup_bp.route('/network')
@auth.login_required
def network():
    """Art-Net network settings"""
    config = get_config()
    return render_template('setup/network.html', config=config)

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
    return render_template('setup/scenes.html', config=config)

# API endpoints for setup

@setup_bp.route('/api/config', methods=['GET'])
@auth.login_required
def get_config_endpoint():
    """Get current configuration, plus the scene limit the editor enforces"""
    config = dict(get_config())
    config['MAX_SCENES'] = current_app.config['MAX_SCENES']
    return jsonify(config)

@setup_bp.route('/api/config/network', methods=['POST'])
@auth.login_required
def update_network_config():
    """Update Art-Net network settings"""
    data = get_json_object()
    if data is None:
        return jsonify({'success': False, 'message': 'JSON body required'}), 400

    artnet_ip = data.get('artnet_ip', '255.255.255.255')
    if not isinstance(artnet_ip, str) or not artnet_ip.strip():
        return jsonify({'success': False, 'message': 'Art-Net IP address is required'}), 400

    # Parse the numeric settings defensively; nothing is saved unless all of
    # them are valid, so a bad value cannot leave configuration half-updated.
    numeric_settings = {
        'artnet_port': (data.get('artnet_port', 6454), 1, 65535),
        'universe': (data.get('universe', 0), 0, 32767),
        'refresh_rate': (data.get('refresh_rate', 30), 1, 60),
    }

    network_config = {'artnet_ip': artnet_ip.strip()}
    for key, (raw, minimum, maximum) in numeric_settings.items():
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': f'{key} must be a number'}), 400
        if not minimum <= value <= maximum:
            return jsonify({
                'success': False,
                'message': f'{key} must be between {minimum} and {maximum}'
            }), 400
        network_config[key] = value

    success = save_config(network_config)
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Failed to save network settings'}), 500

@setup_bp.route('/api/config/fixtures', methods=['POST'])
@auth.login_required
def update_fixtures():
    """Update fixture configuration"""
    data = request.json
    if 'fixtures' not in data:
        return jsonify({'success': False, 'message': 'No fixtures provided'}), 400
    
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

    invalid = find_invalid_channel(data['channels'])
    if invalid:
        return jsonify({'success': False, 'message': invalid}), 400

    # Get enabled fixtures (optional)
    enabled_fixtures = data.get('enabledFixtures', None)
    group = data.get('group', None)

    success = save_scene(data['name'], data['channels'], enabled_fixtures, group)
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

    invalid = find_invalid_channel(data['channels'])
    if invalid:
        return jsonify({'success': False, 'message': invalid}), 400

    success = test_scene(data['channels'])
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
