# 🎬 AI Director System

## Overview

L'**AI Director** è il cervello intelligente che orchestra lo spettacolo di luci in tempo reale. Non si limita a cambiare effetto ogni X secondi, ma **capisce la musica** e prende decisioni intelligenti millisecondo per millisecondo.

## Come Funziona

```
Audio Stream → AudioAnalyzer
                    ↓
            MusicIntelligence ← Shazam (genre, metadata)
                    ↓
            MusicStructureAnalyzer (rileva build-up, drop, breakdown)
                    ↓
              AI Director (prende decisioni)
                    ↓
              EffectEngine (esegue)
                    ↓
              WiZ Lights
```

## 🎭 Music Structure Analyzer

Analizza la struttura della musica in tempo reale e rileva:

### Momenti Speciali
- **Drop** 💥 - Esplosione di energia (energia spike + alta energia)
- **Pre-Drop** ⚠️ - Drop imminente (build-up forte, probabilità >85%)
- **Build-up** 🌊 - Tensione crescente (energia in aumento progressivo)
- **Breakdown** 🌊 - Momento emotivo/calmo (energia cala improvvisamente)
- **High Energy** ⚡ - Energia costante alta (>0.7)
- **Low Energy** 🌙 - Energia bassa (<0.3)

### Parametri Tracciati
- **Energy History** - Ultimi 5 secondi di energia
- **Beat Intervals** - Timing dei beat (rileva four-on-floor)
- **Emotional Intensity** - Livello emotivo 0-1
- **Emotional Valence** - Positivo/negativo basato su frequenze
- **Urgency** - Quanto urgente è cambiare effetto (0-1)

## 🎬 AI Director

Il regista che prende decisioni in real-time basandosi sui dati analizzati.

### Strategie di Decisione

#### 1. Urgent Decisions (Priorità Massima)
Decisioni critiche prese immediatamente quando rileva:

**DROP EXPLOSION** 💥
```python
Effetti: Center Expand, Cascade Strobe, Energy Pulse, Peak Time
Intensità: 1.0 (MASSIMA)
Color Mood: explosive
Azione: Impatto massimo
```

**PRE-DROP TENSION** ⚠️
```python
Effetti: Invasion Wave, Strobe Zones, Chase Around
Intensità: 0.9
Color Mood: tense
Azione: Costruire anticipazione
```

**BREAKDOWN CALM** 🌊
```python
Effetti: Welcome Flow, Bottle Showcase, Rainbow Flow
Intensità: 0.4
Color Mood: calm
Azione: Atmosfera emotiva e calma
```

#### 2. Adaptive Decisions
Decisioni adattive basate sul momento attuale:

| Momento | Effetti Preferiti | Durata | Intensità |
|---------|-------------------|---------|-----------|
| Drop | Center Expand, Energy Pulse, Peak Time | 15s | 0.9-1.0 |
| Build-up | Invasion Wave, Party Wave, Chase | 15-30s | 0.7-1.0 |
| High Energy | Party Wave, Strobe Zones, Chase | 30s | 0.8-1.0 |
| Breakdown | Welcome Flow, Bottle Showcase | 60s | 0.3-0.6 |
| Low Energy | Bar Mode, Welcome Flow | 45s | 0.4-0.7 |
| Normal | Ping Pong, Perimeter Chase | 30s | 0.6-0.9 |

### Intelligent Features

1. **Avoid Repetition** - Non ripete gli ultimi 5 effetti usati
2. **Moment-Aware** - Sceglie effetti appropriati al momento
3. **Dynamic Intensity** - Intensità che si adatta in real-time:
   - +30% boost durante drops
   - +20% boost progressivo durante build-up
   - -50% riduzione durante breakdown
   - +10% pulse sui beat

4. **Color Evolution** - Suggerisce come i colori devono evolvere:
   - Should pulse: Durante drop o four-on-floor
   - Should fade: Durante breakdown
   - Should strobe: Drop intenso (>0.8)

## 🎨 Integration con Color System

L'AI Director imposta il "mood" del ColorSystem che influenza la palette:

| Mood | Effetto | Quando |
|------|---------|--------|
| explosive | Colori vivaci, massima saturazione | Drop |
| tense | Colori cupi, preparazione | Pre-Drop |
| rising | Gradiente crescente | Build-up |
| calm | Colori soft, pastello | Breakdown |
| vibrant | Colori brillanti | High Energy |
| soft | Colori dim, rilassanti | Low Energy |
| balanced | Mix equilibrato | Normal |

## 🚀 Vantaggi

### Prima (Sistema Vecchio)
```
Effetto ogni 45s → AI suggerisce → Cambia
```
- ❌ Timing fisso, non reattivo
- ❌ Cambi solo ogni 45 secondi
- ❌ Non rileva momenti speciali
- ❌ Intensità statica

### Ora (AI Director)
```
Frame (~50ms) → Analizza → Decide → Reagisce
```
- ✅ **Real-time**: Reagisce in millisecondi
- ✅ **Context-aware**: Capisce build-up, drop, breakdown
- ✅ **Dynamic**: Intensità che cambia continuamente
- ✅ **Predictive**: Anticipa i drop prima che arrivino
- ✅ **Emotional**: Segue l'evoluzione emotiva della canzone

## 🎯 Esempi di Scenario

### Scenario 1: Drop Epico
```
T-4s: Build-up rilevato → Invasion Wave con intensità crescente
T-1s: Drop probability 90% → Pre-drop tension mode
T=0s: DROP! → 💥 Center Expand, MASSIMA intensità
      Tutti i LED al massimo, colori esplosivi
T+4s: Mantenimento energia → Continua Center Expand
T+8s: Energia cala → Transition a Party Wave
```

### Scenario 2: Breakdown Emotivo
```
T=0s: Energia cala da 0.8 → 0.3 → Breakdown rilevato
      🌊 Passa a Welcome Flow
      Colori soft, palette pastello
      Intensità 0.4
T+30s: Rimane in Welcome Flow (breakdown può durare)
T+60s: Energia ritorna → Adaptive transition
```

### Scenario 3: Four-on-Floor Dance
```
Pattern rilevato: Beat ogni 0.5s, costante
Momento: High Energy
AI Director: Party Wave con pulse sui beat
Colori: Palette vibrant che pulsa ogni beat
Durata: 30s di energia costante
```

## 🎛️ Configurazione

Abilita/Disabilita AI Director:
```python
self.ai_director_enabled = True  # In EffectEngine.__init__
```

Parametri regolabili in `MusicStructureAnalyzer`:
```python
self.energy_history = deque(maxlen=100)  # 5s history
# Threshold per build-up detection
energy_growth > 0.15  # 15% increase

# Threshold per drop detection
energy_spike > 0.3 and recent_avg > 0.7

# Threshold per breakdown
energy_drop > 0.2 and recent_avg < 0.4
```

Parametri in `AIDirector`:
```python
self.min_effect_duration = 15  # Drop/buildup
self.max_effect_duration = 60  # Breakdown
self.adaptive_duration = 30    # Normal
```

## 🐛 Debug

Il sistema stampa informazioni ogni 10 secondi:
```
============================================================
🎨 💥 Center Expand
⏱️  23s
📊 Bass=0.78 Energy=0.85
🎵 🔊 PLAYING
🧠 Section: drop | Emotion: excited | Energy: HIGH
🎭 Section: drop (0.90) | Moment: drop | Urgency: 1.00 | 💥 DROP!
🎬 Moment: drop (1.00) | Last: 💥 Center Expand (ai_recommended)
🎼 Artist - Song Title
============================================================
```

## 🔮 Future Enhancements

Possibili miglioramenti futuri:
1. **ML-based prediction** - Machine learning per predire drop ancora prima
2. **Crowd feedback** - Input da sensori per capire reazione del pubblico
3. **Genre-specific strategies** - Strategie diverse per EDM vs Rock vs Hip-Hop
4. **Cross-song transitions** - Transizioni intelligenti tra canzoni
5. **Lyric-driven moments** - Reazioni a parole chiave nei testi
6. **BPM-locked timing** - Tutto perfettamente sincronizzato con il BPM

---

**Status**: ✅ Implementato e funzionante
**Version**: 1.0
**Created**: 2026-01-27
