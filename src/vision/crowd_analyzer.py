"""
Crowd Analyzer - Vision layer per Jetson
=========================================
Analizza il video della sala in tempo reale per capire:
- Quante persone ci sono e dove
- Quanto stanno ballando (energia movimento)
- Qual è la zona più attiva
- L'emozione generale della folla

Richiede: opencv, ultralytics (YOLOv8)
TODO: implementazione completa nel prossimo sprint
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CrowdState:
    """Stato corrente della sala rilevato dalla videocamera."""
    crowd_count: int = 0                  # Numero persone rilevate
    crowd_energy: float = 0.0             # 0.0 (fermi) → 1.0 (tutti ballano)
    active_zone: str = "unknown"          # Zona più attiva: pista/bar/corridoio
    zone_density: dict = field(default_factory=dict)  # Persone per zona
    dominant_emotion: str = "neutral"     # Emozione rilevata dalla folla
    is_dancing: bool = False              # C'è gente che balla?
    timestamp: float = field(default_factory=time.time)


class CrowdAnalyzer:
    """
    Analizza il feed video della videocamera per estrarre
    lo stato della sala in tempo reale.

    Pipeline:
        frame → YOLOv8 detect persone → optical flow → crowd state
    """

    def __init__(self, config: dict):
        self.config = config
        self.camera_index = config.get('vision', {}).get('camera_index', 0)
        self.enabled = config.get('vision', {}).get('enabled', False)
        self._state = CrowdState()
        self._running = False

        # TODO: inizializzare modello YOLOv8 e OpenCV

    async def start(self):
        """Avvia il loop di analisi video in background."""
        if not self.enabled:
            logger.info("Vision layer disabilitato in config - skip")
            return
        self._running = True
        logger.info("CrowdAnalyzer avviato (stub - da implementare)")
        # TODO: loop asyncio con cv2.VideoCapture

    async def stop(self):
        self._running = False

    def get_crowd_state(self) -> CrowdState:
        """Restituisce l'ultimo stato crowd rilevato."""
        return self._state

    # ─── TODO: implementare ────────────────────────────────────────────────────
    # def _detect_people(self, frame) -> list:          # YOLOv8 inference
    # def _calc_optical_flow(self, prev, curr) -> float: # movimento/energia
    # def _map_zone(self, bbox) -> str:                  # bbox → zona sala
    # def _estimate_emotion(self, faces) -> str:         # face emotion
