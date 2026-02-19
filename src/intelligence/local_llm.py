"""
Local LLM - Art Director emotivo delle luci
=============================================
Usa Ollama (Mistral / Llama 3.2) in locale sul Jetson per generare
un "lighting score": una partitura emotiva che guida il real-time engine.

NON sceglie un effetto da una lista — genera un'intenzione emotiva strutturata
che il EffectEngine poi esegue frame per frame in tempo reale.

Esempio di lighting score generato:
{
    "emotional_palette": {
        "core_emotion": "euphoric",
        "secondary": "anticipation",
        "metaphor": "pioggia di neon su asfalto bagnato"
    },
    "color_language": {
        "primary_hue": "cool_cyan",
        "accent_hue": "electric_violet",
        "warmth": "cold",
        "saturation": "very_saturated",
        "brightness_dynamic": "pulse_with_beat"
    },
    "rhythm_behavior": {
        "on_beat": "sharp_flash",
        "on_drop": "full_room_white_burst",
        "on_break": "fade_to_dark_ambient",
        "on_buildup": "chase_expanding_from_dj"
    },
    "zone_emotion": {
        "pista": "protagonist",
        "bar": "supporting",
        "corridoio": "ambient",
        "dj": "heartbeat"
    },
    "transition_feel": "sharp",
    "reasoning": "Sandstorm è euforia pura, elettrica e fredda..."
}
"""

import json
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

# Prompt di sistema — definisce il "carattere" dell'art director
SYSTEM_PROMPT = """Sei un art director di luci per una serata in un locale.
Il tuo compito è leggere la situazione della sala — la musica, il genere, i testi,
l'energia della folla — e tradurla in un'intenzione emotiva per le luci.

NON scegli effetti tecnici. Descrivi come deve SENTIRSI la sala.
Rispondi SEMPRE con un JSON valido nel formato richiesto, senza testo aggiuntivo.
Ragiona in termini di emozioni, colori, atmosfera, metafore visive."""

LIGHTING_SCORE_PROMPT = """Analizza questa situazione e genera il lighting score:

{scene_context}

Genera un JSON con questa struttura esatta:
{{
    "emotional_palette": {{
        "core_emotion": "una parola (euphoric/melancholic/intense/playful/dark/hopeful/sensual/wild)",
        "secondary": "una parola",
        "metaphor": "una frase poetica che descrive l'atmosfera visiva"
    }},
    "color_language": {{
        "primary_hue": "una di: warm_red/orange/golden/cool_cyan/electric_blue/violet/pink/white/deep_purple/acid_green",
        "accent_hue": "una di quelle sopra",
        "warmth": "warm/neutral/cold",
        "saturation": "desaturated/medium/saturated/very_saturated",
        "brightness_dynamic": "una di: pulse_with_beat/slow_breathe/steady/chase_on_beat/strobe_on_drop"
    }},
    "rhythm_behavior": {{
        "on_beat": "sharp_flash/soft_pulse/color_shift/nothing",
        "on_drop": "full_room_white_burst/color_explosion/strobe_burst/nothing",
        "on_break": "fade_to_dark_ambient/slow_color_shift/nothing",
        "on_buildup": "chase_expanding_from_dj/brightness_rise/color_tension/nothing"
    }},
    "zone_emotion": {{
        "pista": "protagonist/supporting/ambient/off",
        "bar": "protagonist/supporting/ambient/off",
        "corridoio": "protagonist/supporting/ambient/off",
        "dj": "protagonist/supporting/ambient/heartbeat"
    }},
    "transition_feel": "sharp/smooth/explosive/subtle",
    "reasoning": "2-3 frasi che spiegano la scelta emotiva"
}}"""


class LocalLLM:
    """
    Art director AI basato su LLM locale (Ollama).
    Genera lighting scores emotivi basati sul contesto della sala.
    """

    def __init__(self, config: dict):
        self.config = config
        llm_config = config.get('intelligence', {}).get('local_llm', {})
        self.model = llm_config.get('model', 'mistral')
        self.enabled = llm_config.get('enabled', False)
        self.fallback_to_gemini = llm_config.get('fallback_to_gemini', True)
        self._client = None
        self._last_score: Optional[dict] = None

    async def initialize(self):
        """Inizializza il client Ollama."""
        if not self.enabled:
            logger.info("LLM locale disabilitato in config")
            return
        try:
            import ollama
            # Verifica che il modello sia disponibile
            models = ollama.list()
            available = [m['name'] for m in models.get('models', [])]
            if self.model not in available and f"{self.model}:latest" not in available:
                logger.warning(
                    f"Modello '{self.model}' non trovato in Ollama. "
                    f"Disponibili: {available}. "
                    f"Esegui: ollama pull {self.model}"
                )
                self.enabled = False
                return
            self._client = ollama
            logger.info(f"LLM locale pronto: {self.model}")
        except ImportError:
            logger.warning("Pacchetto 'ollama' non installato. LLM locale disabilitato.")
            self.enabled = False
        except Exception as e:
            logger.warning(f"Ollama non disponibile: {e}. LLM locale disabilitato.")
            self.enabled = False

    async def generate_lighting_score(self, scene_context) -> Optional[dict]:
        """
        Genera un lighting score emotivo dal contesto della sala.

        Args:
            scene_context: SceneContext con dati audio + vision

        Returns:
            dict con il lighting score, o None se fallisce
        """
        if not self.enabled or not self._client:
            return None

        prompt = LIGHTING_SCORE_PROMPT.format(
            scene_context=scene_context.to_prompt_text()
        )

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.7, "num_predict": 500}
                )
            )

            raw = response['message']['content'].strip()

            # Estrai JSON dalla risposta
            score = self._parse_json(raw)
            if score:
                self._last_score = score
                logger.info(
                    f"Lighting score generato: {score.get('emotional_palette', {}).get('core_emotion')} | "
                    f"{score.get('emotional_palette', {}).get('metaphor', '')}"
                )
                return score

        except Exception as e:
            logger.error(f"Errore generazione lighting score: {e}")

        return None

    def get_last_score(self) -> Optional[dict]:
        """Restituisce l'ultimo lighting score valido."""
        return self._last_score

    def _parse_json(self, text: str) -> Optional[dict]:
        """Estrae e valida il JSON dalla risposta del modello."""
        # Prova parsing diretto
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Cerca blocco JSON delimitato da ```
        import re
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Cerca primo { ... } nel testo
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning(f"Impossibile parsare JSON dalla risposta LLM:\n{text[:200]}")
        return None
