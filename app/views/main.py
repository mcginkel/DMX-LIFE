"""
Main views for the application
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from app import auth
from app.dmx_controller import (
    get_active_scene, get_active_scenes, get_available_scenes, activate_scene,
    get_current_dmx_values, get_highest_active_idx, get_connection_status, get_config
)

main_bp = Blueprint('main', __name__)

# Display order and labels for scene groups on the main page
GROUP_ORDER = [
    ('main', 'Main'),
    ('achtergrond', 'Achtergrond'),
    ('sfeer', 'Sfeer'),
    ('aanuit', 'Alles Aan / Uit'),
]


def get_grouped_scenes():
    """Organize scenes into their display groups, plus ungrouped scenes separately"""
    scenes = get_config().get('scenes', [])
    by_group = {key: [] for key, _ in GROUP_ORDER}
    extra_scenes = []
    for scene in scenes:
        group = scene.get('group')
        if group in by_group:
            by_group[group].append(scene['name'])
        elif group == 'extra':
            extra_scenes.append(scene['name'])
        else:
            # Legacy/ungrouped scenes still get shown so nothing is lost
            by_group.setdefault('_ungrouped', []).append(scene['name'])

    groups = [(key, label, by_group[key]) for key, label in GROUP_ORDER if by_group[key]]
    if by_group.get('_ungrouped'):
        groups.append(('_ungrouped', 'Other', by_group['_ungrouped']))
    return groups, extra_scenes


@main_bp.route('/')
@auth.login_required
def index():
    """Main page with scene selection"""
    groups, extra_scenes = get_grouped_scenes()
    active_scenes = get_active_scenes()
    return render_template('index.html', groups=groups, extra_scenes=extra_scenes, active_scenes=active_scenes)

@main_bp.route('/api/scenes')
@auth.login_required
def list_scenes():
    """API endpoint to list available scenes"""
    return jsonify({
        'scenes': get_available_scenes(),
        'active': get_active_scene(),
        'active_scenes': get_active_scenes()
    })

@main_bp.route('/api/scenes/activate', methods=['POST'])
@auth.login_required
def activate_scene_endpoint():
    """API endpoint to toggle a scene on/off. Returns every scene that is
    currently active (across all groups) so the frontend can resync all
    button highlights, not just the one that was clicked."""
    scene_name = request.json.get('scene')
    if not scene_name:
        return jsonify({'success': False, 'message': 'Scene name required'}), 400

    success, active_scenes = activate_scene(scene_name)
    if success:
        return jsonify({'success': True, 'active_scenes': active_scenes})
    return jsonify({'success': False, 'message': 'Failed to activate scene'}), 500

@main_bp.route('/api/dmx/values')
@auth.login_required
def dmx_values():
    """API endpoint to get current DMX channel values"""

    highest_active_idx = get_highest_active_idx()
    active_scenes = get_active_scenes()
    current_values = get_current_dmx_values()

    # Return all channels up to the highest active one, plus metadata
    values = [int(v) for v in current_values[:highest_active_idx + 1]]

    return jsonify({
        'values': values,
        'highest_active': highest_active_idx,
        'active_scene': active_scenes[-1] if active_scenes else None,
        'active_scenes': active_scenes
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
