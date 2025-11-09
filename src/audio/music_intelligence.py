"""
Music Intelligence Engine
Analizza emozione, struttura e dinamica della musica
per scegliere effetti perfetti
"""

import time
import numpy as np
from collections import deque


class MusicIntelligence:
    """Music emotional and structural analyzer"""
    
    def __init__(self):
        # History tracking
        self.energy_history = deque(maxlen=100)  # ~5 secondi a 20fps
        self.bass_history = deque(maxlen=100)
        self.beat_history = deque(maxlen=20)
        
        # Current state
        self.current_emotion = "neutral"
        self.current_section = "unknown"
        self.estimated_bpm = 0
        self.last_drop_time = 0
        self.last_break_time = 0
        
        # Song metadata (from Shazam)
        self.song_genre = None
        self.song_mood = None
        
        print("🧠 Music Intelligence initialized")
    
    def update(self, audio_features):
        """Update intelligence with new audio frame"""
        # Store history
        self.energy_history.append(audio_features['energy'])
        self.bass_history.append(audio_features['bass'])
        
        if audio_features['beat']:
            self.beat_history.append(time.time())
        
        # Analyze current state
        self._detect_emotion()
        self._detect_section()
        self._estimate_bpm()
    
    def set_song_metadata(self, genre, mood=None):
        """Set song info from Shazam"""
        self.song_genre = genre.lower() if genre else None
        self.song_mood = mood
        print(f"🎵 Song context: Genre={genre}, Mood={mood}")
    
    def _detect_emotion(self):
        """Detect current emotional state"""
        if len(self.energy_history) < 20:
            return
        
        recent_energy = list(self.energy_history)[-20:]
        recent_bass = list(self.bass_history)[-20:]
        
        avg_energy = np.mean(recent_energy)
        avg_bass = np.mean(recent_bass)
        energy_variance = np.var(recent_energy)
        
        # Emotional mapping
        if avg_energy > 0.7 and avg_bass > 0.6:
            self.current_emotion = "intense"  # 💥
        elif avg_energy > 0.5 and energy_variance > 0.05:
            self.current_emotion = "energetic"  # ⚡
        elif avg_energy < 0.2:
            self.current_emotion = "calm"  # 😌
        elif avg_bass > 0.7 and avg_energy < 0.5:
            self.current_emotion = "dark"  # 🌑
        elif energy_variance < 0.01:
            self.current_emotion = "steady"  # 📊
        else:
            self.current_emotion = "neutral"  # 😐
    
    def _detect_section(self):
        """Detect song section (intro, verse, chorus, drop, break)"""
        if len(self.energy_history) < 50:
            self.current_section = "intro"
            return
        
        recent_energy = list(self.energy_history)[-50:]
        very_recent = list(self.energy_history)[-10:]
        
        avg_recent = np.mean(recent_energy)
        avg_very_recent = np.mean(very_recent)
        
        energy_change = avg_very_recent - avg_recent
        
        current_time = time.time()
        
        # DROP detection (sudden energy increase)
        if energy_change > 0.3 and avg_very_recent > 0.6:
            self.current_section = "drop"
            self.last_drop_time = current_time
            print("💥 DROP DETECTED!")
        
        # BREAK detection (sudden energy decrease)
        elif energy_change < -0.3 or avg_very_recent < 0.1:
            self.current_section = "break"
            self.last_break_time = current_time
            print("🔇 BREAK DETECTED!")
        
        # BUILDUP detection (gradual increase)
        elif 0.1 < energy_change < 0.3:
            self.current_section = "buildup"
            print("📈 BUILDUP...")
        
        # CHORUS (high stable energy)
        elif avg_very_recent > 0.6 and np.var(very_recent) < 0.05:
            self.current_section = "chorus"
        
        # VERSE (medium stable energy)
        elif 0.3 < avg_very_recent < 0.6:
            self.current_section = "verse"
        
        else:
            self.current_section = "transition"
    
    def _estimate_bpm(self):
        """Estimate BPM from beat history"""
        if len(self.beat_history) < 4:
            return
        
        # Calculate intervals between beats
        beats = list(self.beat_history)
        intervals = [beats[i] - beats[i-1] for i in range(1, len(beats))]
        
        if intervals:
            avg_interval = np.mean(intervals)
            if avg_interval > 0:
                self.estimated_bpm = int(60 / avg_interval)
            else:
                self.estimated_bpm = 0
    
    def get_recommended_effect(self, available_effects):
        """
        Recommend best effect based on current music state
        
        Returns: effect_name or None
        """
        
        # PRIORITY 1: Section-based (structural moments)
        if self.current_section == "drop":
            if time.time() - self.last_drop_time < 3:
                return "💥 Center Expand"  # BOOM!
        
        if self.current_section == "break":
            if time.time() - self.last_break_time < 2:
                return "🍹 Bar Mode"  # Calm down
        
        if self.current_section == "buildup":
            return "🌊 Invasion Wave"  # Build tension
        
        # PRIORITY 2: Emotion-based
        if self.current_emotion == "intense":
            return "⚡ Cascade Strobe"
        
        if self.current_emotion == "energetic":
            return "🔄 Perimeter Chase"
        
        if self.current_emotion == "calm":
            return "✨ Bottle Showcase"
        
        if self.current_emotion == "dark":
            return "💥 Center Expand"
        
        # PRIORITY 3: Genre + BPM based
        if self.song_genre:
            if "edm" in self.song_genre or "house" in self.song_genre:
                if self.estimated_bpm > 130:
                    return "⚡ Cascade Strobe"  # Fast
                else:
                    return "🏓 Ping Pong"  # Medium
            
            if "jazz" in self.song_genre or "blues" in self.song_genre:
                return "🍹 Bar Mode"
            
            if "rock" in self.song_genre or "metal" in self.song_genre:
                return "⚡ Strobe Zones"
        
        # Default: None (let normal rotation happen)
        return None
    
    def should_freeze(self):
        """Should effects freeze? (during breaks)"""
        return (
            self.current_section == "break" and
            time.time() - self.last_break_time < 1.5
        )
    
    def get_effect_intensity(self):
        """Get intensity multiplier for effects (0.0 - 2.0)"""
        if self.current_section == "drop":
            return 2.0  # MAXIMUM!
        elif self.current_section == "buildup":
            return 1.5  # Building...
        elif self.current_section == "break":
            return 0.3  # Soft
        elif self.current_emotion == "intense":
            return 1.8
        elif self.current_emotion == "calm":
            return 0.6
        else:
            return 1.0  # Normal
    
    def get_status_string(self):
        """Get status for debug"""
        return (
            f"🎭 {self.current_emotion.upper()} | "
            f"🎼 {self.current_section.upper()} | "
            f"🥁 {self.estimated_bpm} BPM"
        )
