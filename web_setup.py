#!/usr/bin/env python3
"""
Light Jockey - Web Setup Launcher
Quick launcher for the web configuration interface
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.web.app import app, load_config

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌐 Light Jockey - Web Setup Interface")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open your browser and go to:")
    print("  http://localhost:5040")
    print("  or")
    print("  http://your-raspberry-ip:5040")
    print("\nPress Ctrl+C to stop")
    print("=" * 60 + "\n")

    config = load_config()
    web_config = config.get('web', {})

    app.run(
        host=web_config.get('host', '0.0.0.0'),
        port=web_config.get('port', 5040),
        debug=False
    )
