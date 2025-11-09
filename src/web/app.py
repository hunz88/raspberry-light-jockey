"""Web Interface for Light Jockey"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import asyncio
import yaml
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.lights.wiz_controller import WizController

app = Flask(__name__)
CORS(app)

wiz_controller = None
discovered_lights = []
config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'

def load_config():
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return {}

def save_selected_lights(light_ips):
    try:
        config = load_config()
        if 'lights' not in config:
            config['lights'] = {}
        config['lights']['auto_discover'] = False
        config['lights']['manual_ips'] = light_ips
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return True
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/discover', methods=['POST'])
def discover_lights_sync():
    global wiz_controller, discovered_lights
    try:
        config = load_config()
        wiz_controller = WizController(config.get('lights', {}))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(wiz_controller.discover_lights())
        finally:
            loop.close()
        
        if success:
            manual_ips = config.get('lights', {}).get('manual_ips', [])
            discovered_lights = [
                {'ip': ip, 'name': f"Light {ip.split('.')[-1]}", 'selected': ip in manual_ips}
                for ip in wiz_controller.get_light_ips()
            ]
            return jsonify({'success': True, 'lights': discovered_lights, 'count': len(discovered_lights)})
        return jsonify({'success': False, 'error': 'No lights found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights', methods=['GET'])
def get_lights():
    return jsonify({'success': True, 'lights': discovered_lights})

@app.route('/api/lights/select', methods=['POST'])
def select_lights():
    try:
        light_ips = request.json.get('light_ips', [])
        if save_selected_lights(light_ips):
            for light in discovered_lights:
                light['selected'] = light['ip'] in light_ips
            return jsonify({'success': True, 'message': f'Selected {len(light_ips)} lights'})
        return jsonify({'success': False, 'error': 'Failed to save'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/test/<ip>', methods=['POST'])
def test_light_sync(ip):
    try:
        if not wiz_controller:
            return jsonify({'success': False, 'error': 'Not initialized'}), 400
        light = next((l for l in wiz_controller.lights if l.ip == ip), None)
        if not light:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def flash():
                for _ in range(3):
                    await light.turn_on()
                    await light.set_rgb(255, 255, 255)
                    await light.set_brightness(255)
                    await asyncio.sleep(0.5)
                    await light.set_brightness(50)
                    await asyncio.sleep(0.5)
            loop.run_until_complete(flash())
            return jsonify({'success': True, 'message': 'Flashed'})
        finally:
            loop.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/set-color', methods=['POST'])
def set_color_sync():
    try:
        if not wiz_controller:
            return jsonify({'success': False, 'error': 'Not initialized'}), 400
        data = request.json
        r = int(data.get('r', 255))
        g = int(data.get('g', 0))
        b = int(data.get('b', 0))
        brightness = int(data.get('brightness', 200))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(wiz_controller.set_color(r, g, b, brightness))
            return jsonify({'success': True, 'message': 'Color set'})
        finally:
            loop.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lights/off', methods=['POST'])
def turn_off_lights_sync():
    try:
        if not wiz_controller:
            return jsonify({'success': False, 'error': 'Not initialized'}), 400
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(wiz_controller.turn_off())
            return jsonify({'success': True, 'message': 'Off'})
        finally:
            loop.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    config = load_config()
    app.run(host=config.get('web', {}).get('host', '0.0.0.0'), 
            port=config.get('web', {}).get('port', 5000), debug=False)
