"""
Ollama AI Color Suggester
Usa un modello LLM locale via Ollama - nessuna API key, funziona offline
"""

import requests
import json
import re


class OllamaColorSuggester:
    """AI-powered color suggestion using local Ollama"""

    EFFECT_TYPES = ['strobe', 'rainbow', 'sparkle', 'wave', 'pulse', 'fade', 'static']
    EFFECT_SPEEDS = ['fast', 'slow', 'medium']

    def __init__(self, host='http://localhost:11434', model='orca-mini:3b'):
        self.host = host.rstrip('/')
        self.model_name = model
        self.generate_url = f"{self.host}/api/generate"

        try:
            r = requests.get(f"{self.host}/api/tags", timeout=3)
            r.raise_for_status()
            print(f"🤖 Ollama AI initialized (model: {model} @ {host})")
        except Exception as e:
            print(f"⚠️  Ollama non raggiungibile ({host}): {e}")

    def suggest_colors(self, song_info, metadata=None, audio_features=None):
        try:
            prompt = self._build_prompt(song_info, audio_features)
            print(f"🎨 Asking Ollama ({self.model_name}) for color suggestions...")

            response = requests.post(
                self.generate_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.4,
                        "num_predict": 200
                    }
                },
                timeout=25
            )
            response.raise_for_status()

            response_text = response.json().get('response', '')
            if not response_text.strip():
                return self._get_fallback_suggestion(song_info, audio_features)

            result = self._parse_response(response_text)
            if result:
                print(f"✅ Ollama palette: {result['palette']} | {result['effect_type']} {result['effect_speed']}")
                return result

            return self._get_fallback_suggestion(song_info, audio_features)

        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return self._get_fallback_suggestion(song_info, audio_features)

    def _build_prompt(self, song_info, audio_features):
        title = song_info.get('title', 'Unknown')
        artist = song_info.get('artist', 'Unknown')
        genre = song_info.get('genre', 'Unknown')
        lyrics = song_info.get('lyrics_snippet', '')

        energy_level = "medium"
        if audio_features:
            energy = audio_features.get('energy', 0.5)
            energy_level = "high" if energy > 0.7 else "low" if energy < 0.3 else "medium"

        lyrics_line = f'\nLyrics hint: "{lyrics[:120]}"' if lyrics else ""

        return f"""Bar lighting for: "{title}" by {artist}
Genre: {genre} | Energy: {energy_level}{lyrics_line}

Pick 3 RGB colors that match the mood and vibe. Examples:
- Dance/Party: R:255 G:0 B:200, R:0 G:255 B:255, R:255 G:255 B:0
- Rock/Metal: R:200 G:0 B:0, R:255 G:80 B:0, R:0 G:0 B:180
- Jazz/Soul: R:255 G:140 B:0, R:128 G:0 B:128, R:255 G:220 B:150
- Romantic/Slow: R:200 G:0 B:50, R:255 G:100 B:150, R:255 G:180 B:100
- Happy/Fun: R:255 G:255 B:0, R:255 G:0 B:128, R:0 G:200 B:255

Answer:
Color 1: R:___ G:___ B:___
Color 2: R:___ G:___ B:___
Color 3: R:___ G:___ B:___"""

    def _parse_response(self, text):
        """Try JSON first, then extract from natural language text"""
        # Try JSON parse
        try:
            clean = re.sub(r'```json\n?|```\n?', '', text).strip()
            match = re.search(r'\{.*\}', clean, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if all(k in data for k in ['palette', 'effect_type', 'effect_speed']):
                    palette = self._validate_palette(data['palette'])
                    if palette:
                        return {
                            'palette': palette,
                            'effect_type': data['effect_type'],
                            'effect_speed': data['effect_speed'],
                            'reasoning': data.get('reasoning', '')
                        }
        except Exception:
            pass

        # Extract from natural language: R:255 G:0 B:200 or R: 255, G: 0, B: 200
        colors = re.findall(
            r'[Rr]\s*[=:]\s*(\d+)[,\s]+[Gg]\s*[=:]\s*(\d+)[,\s]+[Bb]\s*[=:]\s*(\d+)',
            text
        )
        # Also try [255, 0, 200] style
        if not colors:
            colors = re.findall(r'\[(\d+),\s*(\d+),\s*(\d+)\]', text)

        palette = []
        for c in colors[:3]:
            r, g, b = int(c[0]), int(c[1]), int(c[2])
            if r <= 255 and g <= 255 and b <= 255:
                palette.append([r, g, b])

        if not palette:
            return None

        # Pad to 3 colors
        while len(palette) < 3:
            palette.append(palette[-1])

        # Extract effect type (check longer names first to avoid partial matches)
        effect_type = 'pulse'
        for ef in self.EFFECT_TYPES:
            if ef in text.lower():
                effect_type = ef
                break

        # Extract speed
        effect_speed = 'medium'
        for sp in self.EFFECT_SPEEDS:
            if sp in text.lower():
                effect_speed = sp
                break

        return {
            'palette': palette,
            'effect_type': effect_type,
            'effect_speed': effect_speed,
            'reasoning': 'extracted from text'
        }

    def _validate_palette(self, palette):
        if not isinstance(palette, list) or len(palette) < 1:
            return None
        result = []
        for color in palette:
            if isinstance(color, list) and len(color) == 3:
                r = max(0, min(255, int(color[0])))
                g = max(0, min(255, int(color[1])))
                b = max(0, min(255, int(color[2])))
                result.append([r, g, b])
        return result if result else None

    def _get_fallback_suggestion(self, song_info, audio_features):
        genre = song_info.get('genre', '').lower()

        genre_palettes = {
            'dance':      [[255, 0, 200], [0, 255, 255], [255, 255, 0]],
            'pop':        [[255, 100, 200], [100, 200, 255], [255, 200, 100]],
            'rock':       [[200, 0, 0], [255, 80, 0], [0, 0, 180]],
            'hard rock':  [[200, 0, 0], [255, 50, 0], [100, 0, 0]],
            'metal':      [[150, 0, 0], [50, 50, 50], [200, 50, 50]],
            'electronic': [[0, 255, 255], [255, 0, 255], [0, 255, 0]],
            'hip hop':    [[150, 0, 200], [200, 150, 0], [0, 200, 150]],
            'r&b':        [[180, 0, 100], [255, 100, 0], [100, 0, 180]],
            'jazz':       [[100, 50, 150], [200, 150, 50], [255, 200, 100]],
            'soul':       [[200, 100, 0], [150, 0, 100], [255, 180, 50]],
            'blues':      [[50, 100, 200], [100, 150, 255], [30, 70, 150]],
            'classical':  [[200, 180, 255], [255, 220, 200], [180, 200, 255]],
            'reggae':     [[255, 200, 0], [0, 200, 0], [200, 0, 0]],
            'country':    [[200, 150, 50], [150, 100, 0], [255, 200, 100]],
            'latin':      [[255, 50, 0], [255, 200, 0], [0, 180, 100]],
            'soundtrack': [[255, 255, 0], [255, 0, 128], [0, 200, 255]],
        }

        palette = None
        for key, pal in genre_palettes.items():
            if key in genre:
                palette = pal
                break
        if palette is None:
            palette = [[255, 0, 100], [0, 150, 255], [100, 255, 50]]

        effect_type = 'pulse'
        effect_speed = 'medium'
        if audio_features:
            energy = audio_features.get('energy', 0.5)
            bpm = audio_features.get('bpm', 120)
            if energy > 0.7 or bpm > 140:
                effect_type = 'strobe'
                effect_speed = 'fast'
            elif energy < 0.3 or bpm < 90:
                effect_type = 'fade'
                effect_speed = 'slow'

        return {
            'palette': palette,
            'effect_type': effect_type,
            'effect_speed': effect_speed,
            'reasoning': f"fallback for genre '{genre}'"
        }
