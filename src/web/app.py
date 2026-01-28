"""Web Interface for Light Jockey - Setup & Control"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import asyncio
import yaml
from pathlib import Path
import sys
import os
import re
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.lights.wiz_controller import WizController

app = Flask(__name__,
            template_folder=str(Path(__file__).parent / 'templates'),
            static_folder=str(Path(__file__).parent / 'static'))
CORS(app)

wiz_controller = None
discovered_lights = []
config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'

# Zone definitions
AVAILABLE_ZONES = [
    {'id': 'dj', 'name': 'DJ Console & TV', 'color': '#FF6B6B'},
    {'id': 'corridor', 'name': 'Corridoio', 'color': '#4ECDC4'},
    {'id': 'salon_left', 'name': 'Salone Sinistra', 'color': '#45B7D1'},
    {'id': 'salon_right', 'name': 'Salone Destra', 'color': '#96CEB4'},
    {'id': 'salon_back', 'name': 'Salone Fondo', 'color': '#FFEAA7'},
    {'id': 'bar_top', 'name': 'Bancone Clienti', 'color': '#DFE6E9'},
    {'id': 'bar_floor_left', 'name': 'Pedana Sx', 'color': '#74B9FF'},
    {'id': 'bar_floor_right', 'name': 'Pedana Dx', 'color': '#A29BFE'},
    {'id': 'strips', 'name': 'Strip LED Bottiglie', 'color': '#FD79A8'},
    {'id': 'extra', 'name': 'Extra', 'color': '#FDCB6E'}
]

def load_config():
    """Load config with environment variable support"""
    try:
        load_dotenv()
        with open(config_path, 'r') as f:
            config_content = f.read()

        # Replace ${VAR_NAME} with environment variables
        def replace_env_var(match):
            var_name = match.group(1)
            value = os.getenv(var_name)
            if value is None:
                return match.group(0)
            return value

        config_content = re.sub(r'\$\{([^}]+)\}', replace_env_var, config_content)
        return yaml.safe_load(config_content)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_config(config):
    """Save config to YAML"""
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# ========================================
# WEB PAGES
# ========================================

@app.route('/')
def index():
    """Main setup page"""
    return render_template('setup.html', zones=AVAILABLE_ZONES)

@app.route('/control')
def control():
    """Live control page"""
    return render_template('control.html')

# ========================================
# API ENDPOINTS
# ========================================

@app.route('/api/discover', methods=['POST'])
def discover_lights():
    """Discover all Wiz lights on network"""
    global wiz_controller, discovered_lights

    try:
        config = load_config()
        wiz_controller = WizController(config.get('lights', {}))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            light_info = loop.run_until_complete(wiz_controller.discover_lights(return_info=True))
        finally:
            loop.close()

        if light_info:
            # Load existing mapping if any
            existing_mapping = config.get('lights', {}).get('light_mapping', [])
            existing_map = {m['mac']: m for m in existing_mapping}

            discovered_lights = []
            for info in light_info:
                mac = info['mac']
                existing = existing_map.get(mac, {})

                discovered_lights.append({
                    'ip': info['ip'],
                    'mac': mac,
                    'name': existing.get('name', f"Light {info['ip'].split('.')[-1]}"),
                    'zone': existing.get('zone', 'unassigned'),
                    'position': existing.get('position', -1)
                })

            return jsonify({
                'success': True,
                'lights': discovered_lights,
                'count': len(discovered_lights)
            })

        return jsonify({'success': False, 'error': 'No lights found'}), 404

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights', methods=['GET'])
def get_lights():
    """Get discovered lights"""
    return jsonify({'success': True, 'lights': discovered_lights})

@app.route('/api/lights/identify', methods=['POST'])
def identify_light():
    """Identify a light (flash RED for 5 seconds)"""
    global wiz_controller

    try:
        if not wiz_controller:
            return jsonify({'success': False, 'error': 'Not initialized'}), 400

        data = request.json
        ip_or_mac = data.get('light')
        duration = data.get('duration', 5)

        if not ip_or_mac:
            return jsonify({'success': False, 'error': 'Missing light parameter'}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(wiz_controller.identify_light(ip_or_mac, duration))
        finally:
            loop.close()

        if success:
            return jsonify({'success': True, 'message': f'Identified light {ip_or_mac}'})
        else:
            return jsonify({'success': False, 'error': 'Failed to identify light'}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/assign', methods=['POST'])
def assign_light():
    """Assign a light to a zone and position"""
    try:
        data = request.json
        mac = data.get('mac')
        name = data.get('name')
        zone = data.get('zone')
        position = data.get('position', 0)

        if not mac or not zone:
            return jsonify({'success': False, 'error': 'Missing mac or zone'}), 400

        # Update discovered_lights
        for light in discovered_lights:
            if light['mac'] == mac:
                light['name'] = name
                light['zone'] = zone
                light['position'] = position
                break

        return jsonify({'success': True, 'message': 'Light assigned'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/save', methods=['POST'])
def save_light_config():
    """Save light configuration to config.yaml"""
    try:
        config = load_config()

        # Create light_mapping from discovered_lights
        light_mapping = []
        for light in discovered_lights:
            if light['zone'] != 'unassigned':
                light_mapping.append({
                    'mac': light['mac'],
                    'name': light['name'],
                    'zone': light['zone'],
                    'position': light['position']
                })

        # Sort by position
        light_mapping.sort(key=lambda x: x['position'])

        # Update config
        if 'lights' not in config:
            config['lights'] = {}

        config['lights']['use_mac_addresses'] = True
        config['lights']['light_mapping'] = light_mapping

        # Save
        if save_config(config):
            return jsonify({
                'success': True,
                'message': f'Saved {len(light_mapping)} lights to config',
                'count': len(light_mapping)
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save config'}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Get available zones"""
    return jsonify({'success': True, 'zones': AVAILABLE_ZONES})

@app.route('/api/test-color', methods=['POST'])
def test_color():
    """Set all lights to a test color"""
    global wiz_controller

    try:
        if not wiz_controller:
            return jsonify({'success': False, 'error': 'Not initialized'}), 400

        data = request.json
        r = int(data.get('r', 255))
        g = int(data.get('g', 255))
        b = int(data.get('b', 255))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(wiz_controller.set_color(r, g, b, 200))
        finally:
            loop.close()

        if success:
            return jsonify({'success': True, 'message': 'Color set'})
        else:
            return jsonify({'success': False, 'error': 'Failed'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/off', methods=['POST'])
def turn_off_all():
    """Turn off all lights"""
    global wiz_controller

    try:
        if not wiz_controller:
            return jsonify({'success': False, 'error': 'Not initialized'}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(wiz_controller.turn_off())
        finally:
            loop.close()

        if success:
            return jsonify({'success': True, 'message': 'Lights off'})
        else:
            return jsonify({'success': False, 'error': 'Failed'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    config = load_config()
    web_config = config.get('web', {})

    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5040)

    print(f"\n{'='*60}")
    print(f"🌐 Light Jockey Web Interface")
    print(f"{'='*60}")
    print(f"   Access at: http://{host}:{port}")
    print(f"   Setup: http://{host}:{port}/")
    print(f"   Control: http://{host}:{port}/control")
    print(f"{'='*60}\n")

    app.run(host=host, port=port, debug=False)
