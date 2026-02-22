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
                        "temperature": 0.7,
                        "num_predict": 256
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
        """Build prompt for Ollama"""

        prompt = f"""Analyze this song and suggest a color palette for RGB lighting.

**Song Information:**
- Title: {song_info.get('title', 'Unknown')}
- Artist: {song_info.get('artist', 'Unknown')}
- Genre: {song_info.get('genre', 'Unknown')}
"""

        if metadata:
            if metadata.get('lyrics_snippet'):
                prompt += f"\n**Lyrics (excerpt):**\n{metadata['lyrics_snippet'][:200]}...\n"

            if metadata.get('themes'):
                themes_str = ', '.join(metadata['themes'][:3])
                prompt += f"\n**Detected Themes:** {themes_str}\n"

        if audio_features:
            prompt += f"\n**Audio Characteristics:**"
            if 'bpm' in audio_features and audio_features['bpm'] > 0:
                prompt += f"\n- BPM: {audio_features['bpm']}"
            if 'energy' in audio_features:
                energy_level = "high" if audio_features['energy'] > 0.7 else "medium" if audio_features['energy'] > 0.3 else "low"
                prompt += f"\n- Energy: {energy_level}"

        prompt += """

**Task:**
Suggest an RGB lighting scheme that matches the song's mood, theme, and energy.

**Requirements:**
1. Provide 3-5 colors in RGB format (values 0-255)
2. Choose effect type: "wave", "strobe", "pulse", "fade", "static", "rainbow", "sparkle"
3. Set effect speed: "slow", "medium", "fast"
4. Explain your reasoning briefly

**Color Guidelines:**
- Water/Ocean themes → Blues, teals, aqua
- Fire/Energy → Reds, oranges, yellows
- Nature/Forest → Greens, browns, earth tones
- Night/Mystery → Purples, deep blues, dark colors
- Love/Romance → Pinks, reds, warm colors
- Sadness → Blues, grays, cool tones
- Happiness → Yellows, bright colors, warm tones
- Electronic/Party → Vibrant, saturated colors

**Response Format (JSON only, no other text):**
```json
{
  "palette": [[R,G,B], [R,G,B], [R,G,B]],
  "effect_type": "wave",
  "effect_speed": "medium",
  "reasoning": "brief explanation"
}
```"""

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
