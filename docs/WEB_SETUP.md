# 🌐 Plancia Web - Setup Luci con MAC Address

## Panoramica

La plancia web permette di configurare facilmente tutte le 31 luci WiZ del bar usando i **MAC address** invece degli IP, risolvendo i problemi di DHCP.

## 🚀 Avvio Rapido

```bash
python3 web_setup.py
```

Poi apri il browser su:
- **Locale**: http://localhost:5040
- **Rete**: http://192.168.x.x:5040 (IP del Raspberry)
- **Tailscale**: http://your-tailscale-ip:5040

---

## 📋 Guida Passo-Passo

### 1. Avvia la Plancia Web

```bash
cd /path/to/raspberry-light-jockey
python3 web_setup.py
```

### 2. Scopri le Luci

1. Apri il browser sulla pagina principale
2. Clicca **"Scopri Luci sulla Rete"**
3. Aspetta... troverà tutte le luci WiZ

### 3. Identifica Ogni Luce

Per ogni luce trovata:

1. Clicca il bottone **"Identifica (5s)"**
2. La luce lampeggerà in **ROSSO per 5 secondi**
3. Guarda quale luce sta lampeggiando
4. Segna fisicamente la luce o ricordati la posizione

**Esempio:**
```
Luce MAC: a4:cf:12:ab:cd:01 → Lampeggia → È la luce sinistra del DJ!
```

### 4. Assegna Zona e Nome

Per ogni luce:

1. **Nome**: Dai un nome descrittivo
   - `DJ Console - Sinistra 1`
   - `Salone - Prima Destra`
   - `Bar Pedana - Sx 3`

2. **Zona**: Seleziona dal menu a tendina
   - `dj` - DJ Console & TV
   - `salon_left` - Salone Sinistra
   - `bar_top` - Bancone Clienti
   - `strips` - Strip LED Bottiglie
   - etc.

3. **Posizione**: Numero progressivo (0, 1, 2, ...)
   - Le luci saranno ordinate in questo modo nel sistema
   - Posizione 0 = prima luce, 1 = seconda, etc.

### 5. Salva Configurazione

1. Clicca **"Salva Configurazione"**
2. La plancia salverà tutto in `config/config.yaml` con questo formato:

```yaml
lights:
  use_mac_addresses: true
  light_mapping:
    - mac: "a4:cf:12:ab:cd:01"
      name: "DJ Console - Sinistra 1"
      zone: "dj"
      position: 0

    - mac: "a4:cf:12:ab:cd:02"
      name: "DJ Console - Sinistra 2"
      zone: "dj"
      position: 1

    # ... altre 29 luci
```

### 6. Testa il Sistema

Prima di uscire dalla plancia:

1. **Test Colore**: Clicca "Test Colore" → Tutte le luci diventeranno bianche
2. **Spegni**: Clicca "Spegni Tutte" → Tutte si spengono
3. Se funziona, sei pronto!

---

## 🎯 Zone Disponibili

| ID | Nome | Descrizione |
|----|------|-------------|
| `dj` | DJ Console & TV | 5 luci console DJ + TV |
| `corridor` | Corridoio | 1 luce transizione |
| `salon_left` | Salone Sinistra | 4 luci lato sinistro |
| `salon_right` | Salone Destra | 4 luci lato destro |
| `salon_back` | Salone Fondo | 1 luce fondo |
| `bar_top` | Bancone Clienti | 4 luci sopra bancone |
| `bar_floor_left` | Pedana Sx | 4 luci pedana sinistra |
| `bar_floor_right` | Pedana Dx | 4 luci pedana destra |
| `strips` | Strip LED Bottiglie | 3 strip LED |
| `extra` | Extra | 1 luce extra |

---

## 🔧 Come Funziona il Sistema MAC

### Problema con IP
```
Prima:
config.yaml → manual_ips: ["192.168.0.153", "192.168.0.22", ...]

Router riavvia → DHCP assegna nuovi IP
192.168.0.153 diventa 192.168.0.200 → CAOS!
Luce DJ diventa luce Bar → Effetti tutti sbagliati!
```

### Soluzione con MAC
```
Ora:
config.yaml → light_mapping con MAC address

All'avvio:
1. Sistema fa discovery di tutte le luci
2. Trova MAC a4:cf:12:ab:cd:01 → Anche se IP è cambiato!
3. Assegna posizione 0 (DJ Console - Sinistra 1)
4. Effetti sempre corretti!
```

**MAC address = Identificativo hardware permanente**
- Non cambia MAI
- Unico per ogni luce
- Indipendente da IP/DHCP

---

## 🎨 Features della Plancia

### ✅ Discovery Automatico
- Trova tutte le luci WiZ sulla rete
- Mostra IP e MAC di ogni luce

### ✅ Identificazione Visiva
- Lampeggio rosso 5 secondi
- Vedi fisicamente quale luce è quale

### ✅ Assegnazione Facile
- Nome personalizzato
- Selezione zona da menu
- Posizione numerica

### ✅ Salvataggio Intelligente
- Crea configurazione con MAC
- Ordinamento automatico per posizione
- Validazione completa

### ✅ Test Rapidi
- Test colore bianco
- Spegnimento di tutte le luci
- Verifica immediata

---

## 🐛 Troubleshooting

### Nessuna Luce Trovata

**Problema**: Discovery non trova luci

**Soluzione**:
1. Verifica che Raspberry e luci siano sulla stessa rete
2. Controlla il firewall
3. Prova a riavviare le luci
4. Verifica config broadcast_address (deve essere `255.255.255.255`)

### Luce Non Risponde a "Identifica"

**Problema**: Luce non lampeggia

**Soluzione**:
1. Verifica che la luce sia accesa
2. Controlla l'IP della luce (potrebbe essere cambiato)
3. Ri-fai il discovery
4. Verifica connessione di rete

### Configurazione Non Salvata

**Problema**: Save fallisce

**Soluzione**:
1. Controlla permessi su `config/config.yaml`
2. Verifica che il file non sia in uso
3. Controlla log della console

### Luci in Ordine Sbagliato

**Problema**: Dopo save, luci nell'ordine sbagliato

**Soluzione**:
1. Controlla il campo "Posizione" di ogni luce
2. Devono essere 0, 1, 2, 3... in ordine
3. Ri-salva con posizioni corrette

---

## 🚀 Prossimi Passi

Dopo aver configurato:

1. **Chiudi la plancia web**
2. **Avvia Light Jockey**:
   ```bash
   python3 main.py
   ```

3. **Verifica**:
   - All'avvio vedrai: "🔐 Using MAC address mapping (31 configured)"
   - Sistema caricherà luci in ordine corretto
   - Effetti funzioneranno perfettamente!

---

## 📊 API Endpoints

Per sviluppatori:

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/api/discover` | POST | Scopri luci sulla rete |
| `/api/lights` | GET | Lista luci scoperte |
| `/api/lights/identify` | POST | Identifica luce (lampeggio) |
| `/api/lights/assign` | POST | Assegna luce a zona |
| `/api/config/save` | POST | Salva configurazione |
| `/api/zones` | GET | Lista zone disponibili |
| `/api/test-color` | POST | Test colore |
| `/api/lights/off` | POST | Spegni tutte |

---

## 🎉 Vantaggi Finali

✅ **Niente più IP hardcoded**
✅ **Luci sempre nell'ordine giusto**
✅ **Configurazione visuale facile**
✅ **Identificazione fisica chiara**
✅ **Resiliente a riavvii router**
✅ **Setup in 10 minuti**

---

**Fatto!** 🎉

Ora hai un sistema professionale di gestione luci che funzionerà sempre, indipendentemente da cambi IP!
