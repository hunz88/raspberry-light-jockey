"""
Ollama AI Color Suggester
Usa un modello LLM locale via Ollama - nessuna API key, funziona offline
"""

import requests
import json
import re


class OllamaColorSuggester:
    """AI-powered color suggestion using local Ollama"""

    def __init__(self, host='http://localhost:11434', model='llama3:8b'):
        self.host = host.rstrip('/')
        self.model_name = model
        self.generate_url = f"{self.host}/api/generate"

        # Verify Ollama is reachable
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=3)
            r.raise_for_status()
            print(f"🤖 Ollama AI initialized (model: {model} @ {host})")
        except Exception as e:
            print(f"⚠️  Ollama non raggiungibile ({host}): {e}")

    def suggest_colors(self, song_info, metadata=None, audio_features=None):
        """
        Suggest color palette and effects for a song

        Args:
            song_info: dict with title, artist, genre
            metadata: optional dict with lyrics, tags, etc.
            audio_features: optional dict with tempo, energy, etc.

        Returns:
            dict with palette, effect_type, effect_speed, reasoning
        """
        try:
            prompt = self._build_prompt(song_info, metadata, audio_features)

            print(f"🎨 Asking Ollama ({self.model_name}) for color suggestions...")

            response = requests.post(
                self.generate_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 150
                    }
                },
                timeout=30
            )
            response.raise_for_status()

            response_text = response.json().get('response', '')

            result = self._parse_response(response_text)

            if result:
                print(f"✅ Ollama suggested palette: {result['palette']}")
                print(f"   Effect: {result['effect_type']} ({result['effect_speed']})")
                return result
            else:
                print("⚠️ Using fallback color palette")
                return self._get_fallback_suggestion(song_info, audio_features)

        except Exception as e:
            print(f"❌ Error getting Ollama suggestions: {e}")
            return self._get_fallback_suggestion(song_info, audio_features)

    def _build_prompt(self, song_info, metadata, audio_features):
        """Build prompt for Ollama - short and direct for small models"""

        title = song_info.get('title', 'Unknown')
        artist = song_info.get('artist', 'Unknown')
        genre = song_info.get('genre', 'Unknown')

        energy_level = "medium"
        bpm_info = ""
        if audio_features:
            energy = audio_features.get('energy', 0.5)
            energy_level = "high" if energy > 0.7 else "low" if energy < 0.3 else "medium"
            bpm = audio_features.get('bpm', 0)
            if bpm > 0:
                bpm_info = f", {int(bpm)} BPM"

        prompt = f"""You are a bar lighting controller. Output ONLY valid JSON, no other text.

Song: "{title}" by {artist}
Genre: {genre}
Energy: {energy_level}{bpm_info}

Color rules:
- Dance/Pop → bright yellows [255,255,0], pinks [255,0,128], cyans [0,255,255]
- Rock/Metal → reds [200,0,0], oranges [255,80,0], deep blue [0,0,180]
- Jazz/Soul → amber [255,140,0], purple [128,0,128], warm white [255,220,150]
- Electronic → neon green [0,255,0], magenta [255,0,255], cyan [0,255,255]
- Romantic/Slow → red [200,0,50], pink [255,100,150], warm [255,180,100]
- Happy/Fun → yellow [255,255,0], orange [255,128,0], lime [128,255,0]
- Soundtrack/Kids → bright mixed, rainbow effect

Output exactly this JSON:
{{"palette": [[R,G,B],[R,G,B],[R,G,B]], "effect_type": "pulse", "effect_speed": "medium", "reasoning": "short"}}

effect_type options: wave, strobe, pulse, fade, static, rainbow, sparkle
effect_speed options: slow, medium, fast"""

        return prompt

    def _parse_response(self, response_text):
        """Parse Ollama's JSON response"""
        try:
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\n?', '', response_text)
            response_text = re.sub(r'```\n?', '', response_text)
            response_text = response_text.strip()

            # Extract first JSON object found
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                response_text = match.group(0)

            data = json.loads(response_text)

            if not all(key in data for key in ['palette', 'effect_type', 'effect_speed']):
                print("⚠️ Missing required fields in AI response")
                return None

            palette = data['palette']
            if not isinstance(palette, list) or len(palette) < 1:
                print("⚠️ Invalid palette format")
                return None

            validated_palette = []
            for color in palette:
                if isinstance(color, list) and len(color) == 3:
                    r = max(0, min(255, int(color[0])))
                    g = max(0, min(255, int(color[1])))
                    b = max(0, min(255, int(color[2])))
                    validated_palette.append([r, g, b])

            if not validated_palette:
                print("⚠️ No valid colors in palette")
                return None

            data['palette'] = validated_palette
            return data

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response was: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            return None

    def _get_fallback_suggestion(self, song_info, audio_features):
        """Fallback color suggestion based on genre and energy"""

        genre = song_info.get('genre', '').lower()

        genre_palettes = {
            'rock': [[200, 0, 0], [100, 0, 0], [255, 50, 0]],
            'electronic': [[0, 255, 255], [255, 0, 255], [0, 255, 0]],
            'pop': [[255, 100, 200], [100, 200, 255], [255, 200, 100]],
            'jazz': [[100, 50, 150], [200, 150, 50], [50, 100, 150]],
            'classical': [[200, 180, 255], [255, 220, 200], [180, 200, 255]],
            'blues': [[50, 100, 200], [100, 150, 255], [30, 70, 150]],
            'metal': [[150, 0, 0], [50, 50, 50], [200, 50, 50]],
            'hip hop': [[150, 0, 200], [200, 150, 0], [0, 200, 150]],
            'reggae': [[255, 200, 0], [0, 200, 0], [200, 0, 0]],
            'country': [[200, 150, 50], [150, 100, 0], [100, 50, 0]]
        }

        palette = None
        for genre_key, genre_palette in genre_palettes.items():
            if genre_key in genre:
                palette = genre_palette
                break

        if palette is None:
            palette = [[255, 0, 100], [0, 150, 255], [100, 255, 50]]

        effect_type = "pulse"
        effect_speed = "medium"

        if audio_features:
            energy = audio_features.get('energy', 0.5)
            bpm = audio_features.get('bpm', 120)

            if energy > 0.7:
                effect_type = "strobe"
                effect_speed = "fast"
            elif energy < 0.3:
                effect_type = "fade"
                effect_speed = "slow"

            if bpm > 140:
                effect_speed = "fast"
            elif bpm < 90:
                effect_speed = "slow"

        return {
            'palette': palette,
            'effect_type': effect_type,
            'effect_speed': effect_speed,
            'reasoning': f"Fallback suggestion based on genre '{genre}'"
        }
