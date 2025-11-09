#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.web.app import app, load_config

if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Light Jockey Web Interface")
    print("=" * 60)
    print()
    config = load_config()
    web_config = config.get('web', {})
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    print(f"🚀 Starting web server...")
    print(f"📱 Open browser: http://192.168.0.201:{port}")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    app.run(host=host, port=port, debug=False)
