"""
Setup views for DMX configuration
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app.dmx_controller import (get_config, save_config, save_scene, delete_scene, test_scene,
                               get_interface_status, get_available_interface_types, 
                               get_interface_info, switch_interface_type)
from app.models.fixture import FixtureType

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/')
def index():
    """Setup main page"""
    return render_template('setup/index.html')

@setup_bp.route('/network')
def network():
    """DMX interface and network settings"""
    config = get_config()
    interface_status = get_interface_status()
    interface_info = get_interface_info()
    return render_template('setup/network.html', 
                          config=config,
                          interface_status=interface_status,
                          interface_info=interface_info)

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
    """Update DMX interface settings"""
    data = request.json
    
    # Get current interface type
    current_config = get_config()
    interface_type = current_config.get('interface_type', 'artnet')
    
    # Prepare config updates based on interface type
    network_config = {'interface_type': interface_type}
    
    if interface_type == 'artnet':
        network_config.update({
            'artnet_ip': data.get('artnet_ip', '255.255.255.255'),
            'artnet_port': int(data.get('artnet_port', 6454)),
            'universe': int(data.get('universe', 0)),
            'refresh_rate': int(data.get('refresh_rate', 30))
        })
    elif interface_type == 'usb_dmx':
        network_config.update({
            'usb_port': data.get('usb_port', 'auto'),
            'usb_baud_rate': int(data.get('usb_baud_rate', 250000)),
            'usb_data_bits': int(data.get('usb_data_bits', 8)),
            'usb_stop_bits': int(data.get('usb_stop_bits', 2)),
            'usb_parity': data.get('usb_parity', 'N'),
            'usb_timeout': float(data.get('usb_timeout', 1.0))
        })
    
    success = save_config(network_config)
    if success:
        return jsonify({'success': True, 'status': get_interface_status()})
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
    
    # Get enabled fixtures (optional)
    enabled_fixtures = data.get('enabledFixtures', None)
    
    success = save_scene(data['name'], data['channels'], enabled_fixtures)
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


@setup_bp.route('/api/config/scenes/test', methods=['POST'])
def test_scene_endpoint():
    """test a scene"""
    data = request.json
    if 'channels' not in data:
        return jsonify({'success': False, 'message': 'Channels required'}), 400
    
    success = test_scene(data['channels'])
    if success:
        return jsonify({'success': True})
    
    
    return jsonify({'success': False, 'message': 'Failed to save scene'}), 500

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

@setup_bp.route('/api/interface/status', methods=['GET'])
def get_interface_status_endpoint():
    """Get current DMX interface status"""
    return jsonify(get_interface_status())

@setup_bp.route('/api/interface/types', methods=['GET'])
def get_interface_types_endpoint():
    """Get available DMX interface types"""
    return jsonify({
        'types': get_available_interface_types(),
        'info': get_interface_info()
    })

@setup_bp.route('/api/interface/switch', methods=['POST'])
def switch_interface_endpoint():
    """Switch DMX interface type"""
    data = request.json
    interface_type = data.get('interface_type')
    
    if not interface_type:
        return jsonify({'success': False, 'message': 'Interface type required'}), 400
        
    if interface_type not in get_available_interface_types():
        return jsonify({'success': False, 'message': 'Invalid interface type'}), 400
    
    config_updates = data.get('config', {})
    success = switch_interface_type(interface_type, config_updates)
    
    if success:
        return jsonify({'success': True, 'status': get_interface_status()})
    return jsonify({'success': False, 'message': 'Failed to switch interface'}), 500

@setup_bp.route('/api/interface/usb-ports', methods=['GET'])
def get_usb_ports_endpoint():
    """Get available USB ports for USB-DMX interface"""
    try:
        # Import here to avoid issues if pyserial is not installed
        from app.dmx_interfaces.usb_dmx import USBDMXInterface
        
        # Create a temporary instance to get port list
        usb_interface = USBDMXInterface({})
        ports = usb_interface.get_available_ports()
        
        return jsonify({'ports': ports})
    except ImportError:
        return jsonify({'ports': [], 'error': 'PySerial not available'})
    except Exception as e:
        return jsonify({'ports': [], 'error': str(e)})
