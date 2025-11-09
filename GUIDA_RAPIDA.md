# 🚀 Guida Rapida - Raspberry Pi Light Jockey

## 📦 Step 1: Ottenere la Gemini API Key (GRATIS!)

1. Vai su: https://makersuite.google.com/app/apikey
2. Accedi con il tuo account Google
3. Clicca su "Create API Key"
4. Copia la chiave generata

**Limiti FREE:**
- 15 richieste al minuto
- 1500 richieste al giorno
- Più che sufficienti per uso personale!

---

## 🔧 Step 2: Installazione sul Raspberry Pi

```bash
# 1. Copia tutto il progetto sul Raspberry Pi
# Puoi usare scp, git, o chiavetta USB

# 2. Vai nella cartella del progetto
cd raspberry-light-jockey

# 3. Esegui lo script di installazione
chmod +x install.sh
./install.sh

# L'installazione richiede 10-15 minuti
# Lo script installerà tutte le dipendenze automaticamente
```

---

## ⚙️ Step 3: Configurazione

```bash
# 1. Copia il file di configurazione
cp config/config.example.yaml config/config.yaml

# 2. Modifica la configurazione
nano config/config.yaml

# 3. Inserisci la tua Gemini API key nella sezione:
#    ai.gemini.api_key: 'LA_TUA_CHIAVE_QUI'

# 4. (Opzionale) Aggiungi gli IP delle tue luci Wiz nella sezione:
#    lights.manual_ips:
#      - '192.168.1.100'
#      - '192.168.1.101'
```

---

## ▶️ Step 4: Avvio

```bash
# Attiva l'ambiente virtuale
source venv/bin/activate

# Avvia il sistema
python3 main.py

# Il sistema:
# ✓ Si connette alle luci Wiz
# ✓ Inizia ad ascoltare l'audio
# ✓ Reagisce alla musica in real-time
# ✓ Riconosce le canzoni ogni 30 secondi
# ✓ Chiede all'AI suggerimenti di colori
```

---

## 🎵 Come Funziona

### Modalità Audio-Reattiva (sempre attiva)
- Le luci reagiscono ai bassi, medi, alti
- Rileva i beat e cambia intensità
- Calcola il BPM automaticamente

### Riconoscimento Canzoni (ogni 30 sec)
1. Cattura 5 secondi di audio
2. Riconosce la canzone con Shazam
3. Scarica testi e metadata
4. Analizza temi e mood

### AI Color Suggester
1. Prende tutte le info sulla canzone
2. Chiede a Gemini una palette colori
3. Suggerisce il tipo di effetto
4. Applica la scena automaticamente

---

## 🎨 Effetti Disponibili

- **pulse**: pulsazione morbida tra i colori
- **wave**: onda di colori fluida
- **strobe**: strobo energico
- **fade**: dissolvenza lenta
- **static**: colore fisso
- **rainbow**: arcobaleno HSV
- **sparkle**: scintille casuali

---

## 🎛️ Personalizzazione Veloce

### Cambiare Sensibilità ai Bassi
```yaml
audio:
  beat_sensitivity: 0.5  # 0.0 = meno sensibile, 1.0 = molto sensibile
```

### Cambiare Velocità Effetti
```yaml
effects:
  update_rate: 30  # FPS (10-60)
  transition_speed: 500  # millisecondi
```

### Intervallo Riconoscimento
```yaml
recognition:
  recognition_interval: 30  # secondi tra riconoscimenti
```

---

## 🐛 Risoluzione Problemi

### Le luci non vengono trovate
```bash
# Controlla che siano sulla stessa rete
ip addr show

# Prova a pingare le luci
ping 192.168.1.100

# Aggiungi gli IP manualmente in config.yaml
```

### Errore "No audio device"
```bash
# Lista dispositivi audio
arecord -l

# Seleziona device specifico in config.yaml
audio:
  input_device: 1  # numero del device
```

### Gemini API non funziona
```bash
# Verifica la chiave API
# Controlla i limiti su: https://makersuite.google.com/app/apikey
# Prova con modalità fallback (funziona senza AI)
```

---

## 📊 Monitoraggio

Mentre il sistema gira vedrai:
```
📊 Bass: 0.45 | Energy: 0.67 | BPM: 128 | ♫ Ocean Eyes
```

Ogni volta che riconosce una canzone:
```
---------------------------------------------------------
🎵 Attempting song recognition...
✅ Recognized: Ocean Eyes - Billie Eilish
📚 Fetching metadata...
🤖 Getting AI color suggestions...

🎨 Applying scene:
   Colors: [[0, 100, 200], [0, 200, 200], [200, 230, 255]]
   Effect: wave (medium)
   Reason: Ocean theme with flowing blues and teals
---------------------------------------------------------
```

---

## 🔄 Aggiornamenti Futuri

Funzionalità pianificate:
- [ ] Web interface per controllo remoto
- [ ] Sistema di learning dalle preferenze
- [ ] Supporto Spotify API
- [ ] Scene personalizzate salvabili
- [ ] Integrazione Home Assistant

---

## 🆘 Supporto

Problemi? Controlla:
1. Tutte le luci sono accese e connesse
2. Microfono funziona: `arecord -d 5 test.wav`
3. API key Gemini è corretta
4. Configurazione YAML è valida

---

## 🎉 Divertiti!

Hai creato un sistema di luci intelligente GRATIS che:
✓ Costa 0€/mese
✓ Riconosce canzoni illimitatamente
✓ Usa AI per suggerimenti creativi
✓ Reagisce alla musica in tempo reale
✓ Impara dalle tue preferenze

**Buon light show! 💡🎵**
