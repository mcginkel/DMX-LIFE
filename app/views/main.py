"""
Main views for the application
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app import auth
from app.dmx_controller import (
    get_active_scene, get_available_scenes, activate_scene, current_dmx_values, 
    get_highest_active_idx, get_connection_status
)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@auth.login_required
def index():
    """Main page with scene selection"""
    scenes = get_available_scenes()
    active_scene = get_active_scene()
    return render_template('index.html', scenes=scenes, active_scene=active_scene)

@main_bp.route('/api/scenes')
@auth.login_required
def list_scenes():
    """API endpoint to list available scenes"""
    return jsonify({
        'scenes': get_available_scenes(),
        'active': get_active_scene()
    })

@main_bp.route('/api/scenes/activate', methods=['POST'])
@auth.login_required
def activate_scene_endpoint():
    """API endpoint to activate a scene"""
    scene_name = request.json.get('scene')
    if not scene_name:
        return jsonify({'success': False, 'message': 'Scene name required'}), 400
    
    success = activate_scene(scene_name)
    if success:
        return jsonify({'success': True, 'active': scene_name})
    return jsonify({'success': False, 'message': 'Failed to activate scene'}), 500

@main_bp.route('/api/dmx/values')
@auth.login_required
def dmx_values():
    """API endpoint to get current DMX channel values"""

    highest_active_idx = get_highest_active_idx()
    active_scene = get_active_scene()

    # Return all channels up to the highest active one, plus metadata
    values = [int(v) for v in current_dmx_values[:highest_active_idx + 1]]
    
    return jsonify({
        'values': values,
        'highest_active': highest_active_idx,
        'active_scene': active_scene
    })

@main_bp.route('/api/connection/status')
@auth.login_required
def connection_status():
    """API endpoint to get Art-Net connection status"""
    status = get_connection_status()
    return jsonify({
        'connected': status['connected'],
        'last_error_time': status['last_error_time'],
        'error_message': status['error_message']
    })
