#!/bin/bash

# =============================================================================
# Sunset Bar DJLuci - Installation Script for NVIDIA Jetson
# =============================================================================
# Compatible with: Jetson Nano, Jetson Orin NX, Jetson AGX Orin
# Carrier board: Yahboom and others
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🎵 Sunset Bar DJLuci - Jetson Setup 🎵              ║"
echo "║         Sistema Luci Intelligente per la Serata              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Detect Jetson platform ───────────────────────────────────────────────────
echo -e "${YELLOW}🔍 Rilevamento piattaforma Jetson...${NC}"

JETSON_MODEL="unknown"
if [ -f /proc/device-tree/model ]; then
    JETSON_MODEL=$(cat /proc/device-tree/model 2>/dev/null || echo "unknown")
fi

if [[ "$JETSON_MODEL" == *"Jetson"* ]]; then
    echo -e "${GREEN}✅ Jetson rilevato: $JETSON_MODEL${NC}"
else
    echo -e "${YELLOW}⚠️  Non sembra un Jetson (trovato: $JETSON_MODEL)${NC}"
    read -p "   Continuare comunque? (s/n) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[SsYy]$ ]] && exit 1
fi

# Check JetPack version
if command -v dpkg &> /dev/null; then
    JETPACK_VER=$(dpkg -l | grep 'nvidia-jetpack' | awk '{print $3}' | head -1)
    if [ -n "$JETPACK_VER" ]; then
        echo -e "${GREEN}✅ JetPack version: $JETPACK_VER${NC}"
    fi
fi

echo ""

# ─── System packages ──────────────────────────────────────────────────────────
echo -e "${YELLOW}📦 Aggiornamento pacchetti di sistema...${NC}"
sudo apt-get update -qq

echo -e "${YELLOW}📦 Installazione dipendenze sistema...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    portaudio19-dev \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    git \
    curl \
    build-essential \
    libhdf5-serial-dev \
    hdf5-tools \
    libhdf5-dev \
    zlib1g-dev \
    zip \
    libjpeg8-dev \
    liblapack-dev \
    libblas-dev \
    gfortran \
    libatlas-base-dev \
    v4l-utils \
    libv4l-dev \
    2>/dev/null || true

echo -e "${GREEN}✅ Dipendenze sistema installate${NC}"
echo ""

# ─── Python virtual environment ───────────────────────────────────────────────
echo -e "${YELLOW}🐍 Configurazione ambiente Python virtuale...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q
echo -e "${GREEN}✅ Virtual environment pronto${NC}"
echo ""

# ─── Python packages ──────────────────────────────────────────────────────────
echo -e "${YELLOW}📦 Installazione pacchetti Python (può richiedere qualche minuto)...${NC}"

# Jetson ha numpy pre-installato, ma usiamo quello nel venv
pip install -r requirements_jetson.txt

echo -e "${GREEN}✅ Pacchetti Python installati${NC}"
echo ""

# ─── Ollama (LLM locale) ──────────────────────────────────────────────────────
echo -e "${YELLOW}🤖 Installazione Ollama (LLM locale)...${NC}"
echo -e "   Ollama permette di girare modelli AI (Mistral, Llama) direttamente sul Jetson"

if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama già installato$(NC)"
else
    if curl -fsSL https://ollama.com/install.sh | sh; then
        echo -e "${GREEN}✅ Ollama installato${NC}"
        echo -e "${YELLOW}💡 Dopo l'installazione, scarica un modello con:${NC}"
        echo -e "   ollama pull mistral"
        echo -e "   oppure: ollama pull llama3.2"
    else
        echo -e "${YELLOW}⚠️  Installazione Ollama fallita - puoi installarla manualmente dopo${NC}"
        echo -e "   curl -fsSL https://ollama.com/install.sh | sh"
    fi
fi
echo ""

# ─── OpenCV with CUDA (opzionale per vision) ──────────────────────────────────
echo -e "${YELLOW}📷 Controllo OpenCV...${NC}"
OPENCV_INSTALLED=false

# Prova prima il pacchetto Jetson pre-compilato
if python3 -c "import cv2; print(cv2.__version__)" 2>/dev/null; then
    CV_VER=$(python3 -c "import cv2; print(cv2.__version__)")
    echo -e "${GREEN}✅ OpenCV già disponibile: $CV_VER${NC}"
    OPENCV_INSTALLED=true
fi

if [ "$OPENCV_INSTALLED" = false ]; then
    echo -e "${YELLOW}   Installazione OpenCV standard (senza CUDA)...${NC}"
    pip install opencv-python-headless 2>/dev/null || true
    echo -e "${YELLOW}   💡 Per OpenCV con supporto CUDA completo, consulta la documentazione Jetson${NC}"
fi
echo ""

# ─── Directory structure ──────────────────────────────────────────────────────
echo -e "${YELLOW}📁 Creazione struttura directory...${NC}"
mkdir -p data
mkdir -p logs
mkdir -p cache
mkdir -p cache/songs
mkdir -p cache/frames
echo -e "${GREEN}✅ Directory create${NC}"
echo ""

# ─── Database ─────────────────────────────────────────────────────────────────
echo -e "${YELLOW}💾 Inizializzazione database...${NC}"
python3 << 'PYEOF'
import sqlite3

db_path = './data/light_jockey.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    genre TEXT,
    mood TEXT,
    shazam_data TEXT,
    lighting_score TEXT,
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
    lighting_score TEXT,
    user_created BOOLEAN DEFAULT 0,
    ai_suggested BOOLEAN DEFAULT 0,
    rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS crowd_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    crowd_count INTEGER,
    crowd_energy REAL,
    active_zone TEXT,
    emotion TEXT
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
print("✅ Database inizializzato!")
PYEOF
echo ""

# ─── Config file ──────────────────────────────────────────────────────────────
if [ ! -f config/config.yaml ]; then
    echo -e "${YELLOW}📝 Creazione file di configurazione...${NC}"
    cp config/config.example.yaml config/config.yaml
    echo -e "${YELLOW}⚠️  IMPORTANTE: Modifica config/config.yaml e aggiungi la tua API key Gemini!${NC}"
fi
echo ""

# ─── Audio device detection ───────────────────────────────────────────────────
echo -e "${YELLOW}🎤 Rilevamento dispositivi audio...${NC}"
python3 << 'PYEOF'
try:
    import pyaudio
    p = pyaudio.PyAudio()
    print("   Dispositivi audio disponibili:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"   [{i}] {info['name']} (input canali: {info['maxInputChannels']})")
    p.terminate()
    print("\n   💡 Annota l'indice del tuo microfono e aggiornalo in config/config.yaml")
except Exception as e:
    print(f"   ⚠️  Errore rilevamento audio: {e}")
PYEOF
echo ""

# ─── Camera detection ─────────────────────────────────────────────────────────
echo -e "${YELLOW}📷 Rilevamento videocamere...${NC}"
python3 << 'PYEOF'
try:
    import cv2
    found = []
    for i in range(4):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            found.append(f"[{i}] {w}x{h}")
            cap.release()
    if found:
        print(f"   ✅ Videocamere trovate: {', '.join(found)}")
        print("   💡 Aggiorna 'vision.camera_index' in config/config.yaml")
    else:
        print("   ⚠️  Nessuna videocamera trovata - verifica il collegamento")
except ImportError:
    print("   ⚠️  OpenCV non disponibile - videocamera non rilevata")
except Exception as e:
    print(f"   ⚠️  Errore rilevamento camera: {e}")
PYEOF
echo ""

# ─── Systemd service ──────────────────────────────────────────────────────────
read -p "Vuoi creare un servizio systemd per avvio automatico? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    WORK_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    SERVICE_FILE="/etc/systemd/system/sunset-djluci.service"

    sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Sunset Bar DJLuci - Sistema Luci Intelligente
After=network.target sound.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WORK_DIR
ExecStart=$WORK_DIR/venv/bin/python3 $WORK_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable sunset-djluci.service
    echo -e "${GREEN}✅ Servizio systemd creato!${NC}"
    echo -e "   Avvia:  sudo systemctl start sunset-djluci"
    echo -e "   Ferma:  sudo systemctl stop sunset-djluci"
    echo -e "   Log:    sudo journalctl -u sunset-djluci -f"
fi

# ─── Final recap ──────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║               ✅ Installazione completata!                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${BOLD}📝 Prossimi passi:${NC}"
echo ""
echo -e "  1. ${YELLOW}API Key Gemini (gratuita):${NC}"
echo -e "     https://makersuite.google.com/app/apikey"
echo ""
echo -e "  2. ${YELLOW}Modifica la configurazione:${NC}"
echo -e "     nano config/config.yaml"
echo ""
echo -e "  3. ${YELLOW}(Opzionale) Scarica LLM locale:${NC}"
echo -e "     ollama pull mistral"
echo ""
echo -e "  4. ${YELLOW}Avvia il sistema:${NC}"
echo -e "     source venv/bin/activate"
echo -e "     python3 main.py"
echo ""
echo -e "  5. ${YELLOW}Web interface:${NC}"
echo -e "     http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo -e "${GREEN}🎉 Buona serata! Il sistema è pronto.${NC}"
echo ""
