"""
Dynamic Color System
Palette intelligenti basate su genere ed emozione
"""

import colorsys
import random


class ColorSystem:
    """Dynamic color palette based on music context"""
    
    def __init__(self):
        # Genre-based color palettes (HSV hues)
        self.genre_palettes = {
            'edm': [0.5, 0.55, 0.6],  # Blu, Cyan, Azzurro
            'house': [0.3, 0.4, 0.5],  # Verde-Cyan
            'techno': [0.8, 0.85, 0.9],  # Viola, Rosa
            'electronic': [0.5, 0.6, 0.7],  # Blu spectrum
            'dance': [0.0, 0.05, 0.1],  # Rosso, Arancio
            'rock': [0.0, 0.05, 0.95],  # Rosso, Rosa shocking
            'metal': [0.95, 0.0, 0.05],  # Rosa-Rosso-Arancio
            'punk': [0.88, 0.92, 0.05],  # Rosa, Fucsia, Arancio
            'pop': [0.8, 0.85, 0.15],  # Rosa, Viola, Giallo
            'hip hop': [0.75, 0.8, 0.0],  # Viola, Rosso
            'rap': [0.0, 0.1, 0.75],  # Rosso, Arancio, Viola
            'trap': [0.85, 0.9, 0.0],  # Viola scuro, Rosa, Rosso
            'jazz': [0.1, 0.15, 0.75],  # Oro, Ambra, Viola
            'blues': [0.55, 0.6, 0.15],  # Blu, Cyan, Oro
            'soul': [0.05, 0.1, 0.75],  # Arancio, Rosso, Viola
            'reggae': [0.3, 0.35, 0.15],  # Verde, Lime, Giallo
            'latin': [0.0, 0.05, 0.15],  # Rosso, Arancio, Giallo
            'default': [0.0, 0.33, 0.66]  # Rosso, Verde, Blu
        }
        
        # Emotion color modifiers
        self.emotion_modifiers = {
            'intense': {'saturation': 1.0, 'value': 1.0},
            'energetic': {'saturation': 0.9, 'value': 1.0},
            'calm': {'saturation': 0.5, 'value': 0.7},
            'dark': {'saturation': 0.8, 'value': 0.6},
            'steady': {'saturation': 0.7, 'value': 0.8},
            'neutral': {'saturation': 0.8, 'value': 0.9}
        }
        
        self.current_palette = self.genre_palettes['default']
        self.current_emotion = 'neutral'
        
        print("🎨 Dynamic Color System initialized")
    
    def set_genre(self, genre):
        """Set color palette based on genre"""
        if not genre:
            return
        
        genre_lower = genre.lower()
        
        # Find matching palette
        for key in self.genre_palettes.keys():
            if key in genre_lower:
                self.current_palette = self.genre_palettes[key]
                print(f"🎨 Palette: {key.upper()} {[f'{h:.2f}' for h in self.current_palette]}")
                return
        
        self.current_palette = self.genre_palettes['default']
    
    def set_emotion(self, emotion):
        """Set emotion for color modulation"""
        self.current_emotion = emotion
    
    def get_primary_color(self, intensity=1.0):
        """Get primary color from current palette"""
        hue = self.current_palette[0]
        mod = self.emotion_modifiers[self.current_emotion]
        
        sat = mod['saturation']
        val = mod['value'] * intensity
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def get_secondary_color(self, intensity=1.0):
        """Get secondary color"""
        hue = self.current_palette[1]
        mod = self.emotion_modifiers[self.current_emotion]
        
        sat = mod['saturation']
        val = mod['value'] * intensity
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def get_accent_color(self, intensity=1.0):
        """Get accent color"""
        hue = self.current_palette[2]
        mod = self.emotion_modifiers[self.current_emotion]
        
        sat = mod['saturation']
        val = mod['value'] * intensity
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def get_complementary(self, intensity=1.0):
        """Get complementary color to primary"""
        hue = (self.current_palette[0] + 0.5) % 1.0
        mod = self.emotion_modifiers[self.current_emotion]
        
        return self.hsv_to_rgb(hue, mod['saturation'], mod['value'] * intensity)
    
    def get_gradient_color(self, position, intensity=1.0):
        """Get color from gradient (position 0.0-1.0)"""
        if position < 0.33:
            # Primary to Secondary
            hue = self.lerp(self.current_palette[0], self.current_palette[1], position * 3)
        elif position < 0.66:
            # Secondary to Accent
            hue = self.lerp(self.current_palette[1], self.current_palette[2], (position - 0.33) * 3)
        else:
            # Accent to Primary
            hue = self.lerp(self.current_palette[2], self.current_palette[0], (position - 0.66) * 3)
        
        mod = self.emotion_modifiers[self.current_emotion]
        return self.hsv_to_rgb(hue, mod['saturation'], mod['value'] * intensity)
    
    def lerp(self, a, b, t):
        """Linear interpolation"""
        return a + (b - a) * t
    
    def hsv_to_rgb(self, h, s, v):
        """HSV to RGB"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)
