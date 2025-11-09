# 🎵 Raspberry Pi Light Jockey - Zero Cost Edition

Sistema completo per controllare luci Wiz RGB con audio-reattività, riconoscimento canzoni e AI per suggerimenti colori intelligenti.

## ✨ Caratteristiche

- 🎵 **Audio Analysis Real-time**: FFT, beat detection, BPM tracking
- 🎼 **Song Recognition**: ShazamIO (illimitato e gratuito!)
- 🤖 **AI Color Suggester**: Gemini API (free tier) o Claude API
- 💡 **Wiz Lights Control**: Supporto completo RGB + dimming
- 🎨 **Smart Scenes**: Colori basati su testi, mood, genere
- 📊 **Learning System**: Impara dalle tue preferenze
- 🌐 **Web Interface**: Controllo da browser/mobile
- 💾 **Database Locale**: Storia e preferenze salvate

## 💰 Costo

**ZERO EURO** - Tutto open source e API gratuite!

## 📋 Requisiti

- Raspberry Pi 3/4/5 (testato su Pi 4)
- Python 3.9+
- Microfono USB o microfono HAT
- Luci Wiz v2 (RGB dimmerabili)
- Connessione Internet (per AI e riconoscimento)

## 🚀 Quick Start

```bash
# 1. Clona o copia il progetto sul Raspberry
cd /home/pi/raspberry-light-jockey

# 2. Esegui lo script di installazione
chmod +x install.sh
./install.sh

# 3. Configura la tua API key Gemini (gratis!)
# Vai su: https://makersuite.google.com/app/apikey
cp config/config.example.yaml config/config.yaml
nano config/config.yaml  # Inserisci la tua API key

# 4. Avvia il sistema
python3 main.py

# 5. Apri il browser
# http://raspberry-ip:5000
```

## 📁 Struttura Progetto

```
raspberry-light-jockey/
├── main.py                 # Entry point
├── install.sh             # Script installazione automatica
├── requirements.txt       # Dipendenze Python
├── config/
│   ├── config.yaml       # Configurazione principale
│   └── config.example.yaml
├── src/
│   ├── audio/
│   │   ├── analyzer.py   # Analisi audio FFT
│   │   └── beat_detector.py
│   ├── recognition/
│   │   ├── shazam_client.py
│   │   └── metadata_fetcher.py
│   ├── ai/
│   │   ├── gemini_suggester.py
│   │   ├── claude_suggester.py (alternativa)
│   │   └── color_mapper.py
│   ├── lights/
│   │   ├── wiz_controller.py
│   │   └── scene_manager.py
│   ├── effects/
│   │   ├── effect_engine.py
│   │   └── transitions.py
│   ├── learning/
│   │   └── preference_system.py
│   └── web/
│       ├── app.py        # Flask server
│       └── static/       # HTML/CSS/JS
└── data/
    ├── scenes.db         # Database SQLite
    └── preferences.db
```

## 🎨 Esempi di Uso

### Modalità Automatica
Il sistema riconosce la canzone, analizza testo/mood e suggerisce automaticamente i colori.

### Modalità Manuale
Scegli tu i colori, il sistema impara e suggerisce meglio la prossima volta.

### Modalità Audio-Reattiva Pura
Nessun riconoscimento, solo reattività pura all'audio (bassi, medi, alti).

## 🔧 Configurazione Avanzata

Vedi `docs/configuration.md` per tutte le opzioni.

## 📝 Note

- Gemini Free Tier: 15 req/min, 1500 req/day (più che sufficienti!)
- ShazamIO: completamente illimitato
- Il sistema funziona anche offline (eccetto AI e riconoscimento)

## 🤝 Contributi

Progetto open source! Migliora e condividi!
