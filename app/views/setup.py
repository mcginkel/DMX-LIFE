"""
Setup views for DMX configuration
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app.dmx_controller import get_config, save_config, save_scene, delete_scene
from app.models.fixture import FixtureType

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/')
def index():
    """Setup main page"""
    return render_template('setup/index.html')

@setup_bp.route('/network')
def network():
    """Art-Net network settings"""
    config = get_config()
    return render_template('setup/network.html', config=config)

@setup_bp.route('/fixtures')
def fixtures():
    """DMX fixture configuration"""
    config = get_config()
    fixture_types = FixtureType.get_types()
    return render_template('setup/fixtures.html', 
                          config=config, 
                          fixture_types=fixture_types)

@setup_bp.route('/scenes')
def scenes():
    """Scene editor"""
    config = get_config()
    return render_template('setup/scenes.html', config=config)

# API endpoints for setup

@setup_bp.route('/api/config', methods=['GET'])
def get_config_endpoint():
    """Get current configuration"""
    return jsonify(get_config())

@setup_bp.route('/api/config/network', methods=['POST'])
def update_network_config():
    """Update Art-Net network settings"""
    data = request.json
    network_config = {
        'artnet_ip': data.get('artnet_ip', '255.255.255.255'),
        'artnet_port': int(data.get('artnet_port', 6454)),
        'universe': int(data.get('universe', 0)),
        'refresh_rate': int(data.get('refresh_rate', 30))
    }
    
    success = save_config(network_config)
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Failed to save network settings'}), 500

@setup_bp.route('/api/config/fixtures', methods=['POST'])
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
def save_scene_endpoint():
    """Create or update a scene"""
    data = request.json
    if not data.get('name') or 'channels' not in data:
        return jsonify({'success': False, 'message': 'Scene name and channels required'}), 400
    
    success = save_scene(data['name'], data['channels'])
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
def delete_scene_endpoint():
    """ Delete a scene"""
    data = request.json
    if not data.get('name') not in data:
        return jsonify({'success': False, 'message': 'Scene name required'}), 400
    
    success = delete_scene(data['name'])
    if success:
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Failed to delete scene'}), 500

@setup_bp.route('/api/fixture-types')
def get_fixture_types():
    """Get available fixture types"""
    return jsonify({
        'types': FixtureType.get_types()
    })

@setup_bp.route('/api/fixture-types/<fixture_type>')
def get_fixture_type_details(fixture_type):
    """Get channel details for a fixture type"""
    channels = FixtureType.get_channels(fixture_type)
    return jsonify({
        'type': fixture_type,
        'channels': channels
    })
