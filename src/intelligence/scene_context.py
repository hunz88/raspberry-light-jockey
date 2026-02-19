"""
Scene Context Aggregator
=========================
Raccoglie dati da tutti i layer (audio + vision) e produce
un contesto unificato della sala che viene passato all'LLM.

Esempio di SceneContext generato:
{
    "song": "Sandstorm - Darude",
    "genre": "electronic",
    "bpm": 136,
    "section": "drop",
    "energy": 0.9,
    "emotion": "euphoric",
    "crowd_count": 42,
    "crowd_energy": 0.8,
    "active_zone": "pista",
    "is_dancing": true
}
"""

import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SceneContext:
    """Snapshot completo della situazione sala in un dato momento."""

    # ── Musica ──────────────────────────────────────────────────────────────
    song_title: str = "unknown"
    song_artist: str = "unknown"
    genre: str = "unknown"
    bpm: float = 0.0
    section: str = "verse"            # verse / chorus / drop / break / buildup
    audio_energy: float = 0.0        # 0.0 → 1.0
    audio_emotion: str = "neutral"   # energetic / calm / intense / euphoric
    lyrics_snippet: str = ""
    song_themes: list = field(default_factory=list)

    # ── Crowd (da vision) ───────────────────────────────────────────────────
    crowd_count: int = 0
    crowd_energy: float = 0.0        # quanto stanno ballando
    active_zone: str = "unknown"
    is_dancing: bool = False
    dominant_emotion: str = "neutral"

    # ── Meta ────────────────────────────────────────────────────────────────
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_prompt_text(self) -> str:
        """Formatta il contesto come testo leggibile per il prompt LLM."""
        dancing_str = "stanno ballando" if self.is_dancing else "fermi/in attesa"
        return (
            f"Canzone: {self.song_title} di {self.song_artist}\n"
            f"Genere: {self.genre} | BPM: {self.bpm:.0f}\n"
            f"Sezione: {self.section} | Energia audio: {self.audio_energy:.2f}\n"
            f"Emozione musica: {self.audio_emotion}\n"
            f"Temi lirici: {', '.join(self.song_themes) if self.song_themes else 'nessuno'}\n"
            f"Folla in sala: {self.crowd_count} persone\n"
            f"Energia folla: {self.crowd_energy:.2f} ({dancing_str})\n"
            f"Zona più attiva: {self.active_zone}\n"
            f"Umore folla: {self.dominant_emotion}"
        )


class SceneContextAggregator:
    """
    Aggrega i dati da AudioAnalyzer e CrowdAnalyzer
    per produrre un SceneContext unificato ogni N secondi.
    """

    def __init__(self, audio_analyzer, crowd_analyzer=None):
        self.audio_analyzer = audio_analyzer
        self.crowd_analyzer = crowd_analyzer
        self._last_context = SceneContext()
        self._current_song: dict = {}

    def update_song(self, song_data: dict, metadata: dict = None):
        """Chiamato quando Shazam riconosce una nuova canzone."""
        self._current_song = song_data
        self._last_context.song_title = song_data.get('title', 'unknown')
        self._last_context.song_artist = song_data.get('artist', 'unknown')
        self._last_context.genre = song_data.get('genre', 'unknown')
        if metadata:
            self._last_context.lyrics_snippet = metadata.get('lyrics', '')[:300]
            self._last_context.song_themes = metadata.get('themes', [])

    def get_current_context(self) -> SceneContext:
        """Restituisce il contesto aggiornato con gli ultimi dati audio e vision."""
        # Aggiorna dati audio
        if self.audio_analyzer:
            features = self.audio_analyzer.get_features()
            if features:
                self._last_context.audio_energy = features.get('energy', 0.0)
                self._last_context.bpm = features.get('bpm', 0.0)
                self._last_context.audio_emotion = features.get('emotion', 'neutral')
                self._last_context.section = features.get('section', 'verse')

        # Aggiorna dati vision (se disponibile)
        if self.crowd_analyzer:
            crowd = self.crowd_analyzer.get_crowd_state()
            self._last_context.crowd_count = crowd.crowd_count
            self._last_context.crowd_energy = crowd.crowd_energy
            self._last_context.active_zone = crowd.active_zone
            self._last_context.is_dancing = crowd.is_dancing
            self._last_context.dominant_emotion = crowd.dominant_emotion

        self._last_context.timestamp = time.time()
        return self._last_context
