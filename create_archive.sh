#!/bin/bash

# Script per creare archivio da trasferire al Raspberry Pi

echo "📦 Creazione archivio per Raspberry Pi..."
echo ""

# Nome archivio
ARCHIVE_NAME="raspberry-light-jockey-$(date +%Y%m%d).zip"

# Vai nella directory corretta
cd "$(dirname "$0")"

# Crea archivio escludendo file non necessari
zip -r "../$ARCHIVE_NAME" . \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "venv/*" \
    -x "data/*" \
    -x "logs/*" \
    -x "cache/*" \
    -x ".git/*" \
    -x "*.zip" \
    -x "config/config.yaml"

echo ""
echo "✅ Archivio creato: $ARCHIVE_NAME"
echo ""
echo "📋 Dimensione:"
du -h "../$ARCHIVE_NAME"
echo ""
echo "🚀 Prossimi step:"
echo ""
echo "1. Trasferisci al Raspberry Pi:"
echo "   scp ../$ARCHIVE_NAME pi@192.168.1.X:~/"
echo ""
echo "2. Sul Raspberry Pi:"
echo "   cd ~"
echo "   unzip $ARCHIVE_NAME"
echo "   cd raspberry-light-jockey"
echo "   chmod +x install.sh"
echo "   ./install.sh"
echo ""
echo "3. Dopo installazione:"
echo "   - Ottieni Gemini API key: https://makersuite.google.com/app/apikey"
echo "   - nano config/config.yaml"
echo "   - Inserisci la tua API key"
echo "   - python3 main.py"
echo ""
echo "🎉 Buon divertimento!"
