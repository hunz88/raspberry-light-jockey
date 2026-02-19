#!/bin/bash

# =============================================================================
# Raspberry Pi Light Jockey - Installation Script
# =============================================================================

set -e  # Exit on error

echo "🎵 Raspberry Pi Light Jockey - Installation Script"
echo "=================================================="
echo ""

# Check if running on supported hardware (Raspberry Pi or Jetson Nano)
IS_RPI=false
IS_JETSON=false

if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    IS_RPI=true
    echo "✅ Raspberry Pi detected"
elif [ -f /etc/nv_tegra_release ] || grep -q -i "tegra\|jetson" /proc/cpuinfo 2>/dev/null; then
    IS_JETSON=true
    echo "✅ NVIDIA Jetson detected"
else
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi or Jetson"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    portaudio19-dev \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    git

# Install Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p cache

# Initialize database
echo "💾 Initializing database..."
python3 << 'PYEOF'
import sqlite3
import os

db_path = './data/light_jockey.db'

# Create database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    genre TEXT,
    mood TEXT,
    shazam_data TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    play_count INTEGER DEFAULT 1
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER,
    name TEXT NOT NULL,
    palette TEXT NOT NULL,
    effect_type TEXT NOT NULL,
    effect_speed TEXT NOT NULL,
    user_created BOOLEAN DEFAULT 0,
    ai_suggested BOOLEAN DEFAULT 0,
    rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER,
    scene_id INTEGER,
    liked BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (scene_id) REFERENCES scenes(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("✅ Database initialized successfully!")
PYEOF

# Copy config file if not exists
if [ ! -f config/config.yaml ]; then
    echo "📝 Creating config file..."
    cp config/config.example.yaml config/config.yaml
    echo "⚠️  IMPORTANT: Edit config/config.yaml and add your Gemini API key!"
    echo "   Get your free API key at: https://makersuite.google.com/app/apikey"
fi

# Discover Wiz lights
echo ""
echo "🔍 Discovering Wiz lights on your network..."
python3 << 'PYEOF'
import asyncio
from pywizlight import discovery

async def discover_lights():
    print("\nSearching for Wiz lights (this may take 10-20 seconds)...")
    try:
        bulbs = await discovery.discover_lights(broadcast_space="255.255.255.255")
        if bulbs:
            print(f"\n✅ Found {len(bulbs)} Wiz light(s):")
            for bulb in bulbs:
                print(f"   - IP: {bulb.ip}")
            print("\nAdd these IPs to config/config.yaml under 'lights.manual_ips' if needed")
        else:
            print("\n⚠️  No Wiz lights found. Make sure they are:")
            print("   1. Powered on")
            print("   2. Connected to the same WiFi network as this Raspberry Pi")
            print("   3. On the same subnet (usually 192.168.1.x)")
    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
        print("You can manually add light IPs in config/config.yaml")

asyncio.run(discover_lights())
PYEOF

# Create systemd service (optional)
echo ""
read -p "Do you want to create a systemd service to auto-start on boot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/light-jockey.service"
    WORK_DIR=$(pwd)
    USER=$(whoami)
    
    sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Raspberry Pi Light Jockey
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
ExecStart=$WORK_DIR/venv/bin/python3 $WORK_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable light-jockey.service
    
    echo "✅ Systemd service created and enabled!"
    echo "   Start with: sudo systemctl start light-jockey"
    echo "   Stop with: sudo systemctl stop light-jockey"
    echo "   View logs: sudo journalctl -u light-jockey -f"
fi

# Final instructions
echo ""
echo "=============================================="
echo "✅ Installation completed successfully!"
echo "=============================================="
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Get your FREE Gemini API key:"
echo "   https://makersuite.google.com/app/apikey"
echo ""
echo "2. Edit the config file:"
echo "   nano config/config.yaml"
echo ""
echo "3. Add your API key to the config file"
echo ""
echo "4. Run the system:"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "5. Open your browser to:"
echo "   http://$(hostname -I | awk '{print $1}'):5040"
echo ""
echo "🎉 Enjoy your smart light show!"
echo ""
