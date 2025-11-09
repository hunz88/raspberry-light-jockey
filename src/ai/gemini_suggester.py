"""
Gemini AI Color Suggester
Uses Google's Gemini API (FREE!) to suggest colors based on song analysis
"""

import google.generativeai as genai
import json
import re


class GeminiColorSuggester:
    """AI-powered color suggestion using Gemini"""
    
    def __init__(self, api_key, model='gemini-pro'):
        self.api_key = api_key
        self.model_name = model
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        
        print(f"🤖 Gemini AI initialized (model: {model})")
    
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
            # Build prompt
            prompt = self._build_prompt(song_info, metadata, audio_features)
            
            print(f"🎨 Asking Gemini for color suggestions...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            result = self._parse_response(response.text)
            
            if result:
                print(f"✅ Gemini suggested palette: {result['palette']}")
                print(f"   Effect: {result['effect_type']} ({result['effect_speed']})")
                return result
            else:
                # Fallback to default
                print("⚠️ Using fallback color palette")
                return self._get_fallback_suggestion(song_info, audio_features)
                
        except Exception as e:
            print(f"❌ Error getting AI suggestions: {e}")
            return self._get_fallback_suggestion(song_info, audio_features)
    
    def _build_prompt(self, song_info, metadata, audio_features):
        """Build prompt for Gemini"""
        
        # Start with basic info
        prompt = f"""Analyze this song and suggest a color palette for RGB lighting.

**Song Information:**
- Title: {song_info.get('title', 'Unknown')}
- Artist: {song_info.get('artist', 'Unknown')}
- Genre: {song_info.get('genre', 'Unknown')}
"""
        
        # Add metadata if available
        if metadata:
            if metadata.get('lyrics_snippet'):
                prompt += f"\n**Lyrics (excerpt):**\n{metadata['lyrics_snippet'][:200]}...\n"
            
            if metadata.get('themes'):
                themes_str = ', '.join(metadata['themes'][:3])
                prompt += f"\n**Detected Themes:** {themes_str}\n"
            
            if metadata.get('genres'):
                genres_str = ', '.join(metadata['genres'])
                prompt += f"\n**Additional Genres:** {genres_str}\n"
        
        # Add audio features if available
        if audio_features:
            prompt += f"\n**Audio Characteristics:**"
            if 'bpm' in audio_features and audio_features['bpm'] > 0:
                prompt += f"\n- BPM: {audio_features['bpm']}"
            if 'energy' in audio_features:
                energy_level = "high" if audio_features['energy'] > 0.7 else "medium" if audio_features['energy'] > 0.3 else "low"
                prompt += f"\n- Energy: {energy_level}"
        
        # Instructions
        prompt += """

**Task:**
Suggest an RGB lighting scheme that matches the song's mood, theme, and energy.

**Requirements:**
1. Provide 3-5 colors in RGB format (values 0-255)
2. Choose effect type: "wave", "strobe", "pulse", "fade", "static", "rainbow", "sparkle"
3. Set effect speed: "slow", "medium", "fast"
4. Explain your reasoning briefly

**Response Format (JSON only):**
```json
{
  "palette": [[R,G,B], [R,G,B], [R,G,B]],
  "effect_type": "wave",
  "effect_speed": "medium",
  "reasoning": "brief explanation of color choices"
}
```

**Color Guidelines:**
- Water/Ocean themes → Blues, teals, aqua
- Fire/Energy → Reds, oranges, yellows
- Nature/Forest → Greens, browns, earth tones
- Night/Mystery → Purples, deep blues, dark colors
- Love/Romance → Pinks, reds, warm colors
- Sadness → Blues, grays, cool tones
- Happiness → Yellows, bright colors, warm tones
- Electronic/Party → Vibrant, saturated colors

Respond ONLY with valid JSON, no other text."""
        
        return prompt
    
    def _parse_response(self, response_text):
        """Parse Gemini's JSON response"""
        try:
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\n?', '', response_text)
            response_text = re.sub(r'```\n?', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Validate structure
            if not all(key in data for key in ['palette', 'effect_type', 'effect_speed']):
                print("⚠️ Missing required fields in AI response")
                return None
            
            # Validate palette
            palette = data['palette']
            if not isinstance(palette, list) or len(palette) < 1:
                print("⚠️ Invalid palette format")
                return None
            
            # Ensure all colors are valid RGB
            validated_palette = []
            for color in palette:
                if isinstance(color, list) and len(color) == 3:
                    # Clamp values to 0-255
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
        
        # Genre-based palettes
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
        
        # Find matching genre
        palette = None
        for genre_key, genre_palette in genre_palettes.items():
            if genre_key in genre:
                palette = genre_palette
                break
        
        # Default colorful palette
        if palette is None:
            palette = [[255, 0, 100], [0, 150, 255], [100, 255, 50]]
        
        # Determine effect based on energy
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
