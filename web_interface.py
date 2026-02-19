#!/usr/bin/env python3
import sys
import socket
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.web.app import app, load_config


def get_local_ip():
    """Get the local network IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Light Jockey Web Interface")
    print("=" * 60)
    print()
    config = load_config()
    web_config = config.get('web', {})
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    local_ip = get_local_ip()
    print(f"🚀 Starting web server...")
    print(f"📱 Open browser: http://{local_ip}:{port}")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    app.run(host=host, port=port, debug=False)
