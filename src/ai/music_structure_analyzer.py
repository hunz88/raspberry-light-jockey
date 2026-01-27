"""
Music Structure Analyzer - Real-time Detection
Detects: build-ups, drops, breakdowns, verses, choruses, bridges
"""

import time
import numpy as np
from collections import deque


class MusicStructureAnalyzer:
    """Analyzes music structure in real-time"""

    def __init__(self):
        # Energy tracking
        self.energy_history = deque(maxlen=100)  # 5 seconds at 20fps
        self.bass_history = deque(maxlen=100)
        self.mid_history = deque(maxlen=100)

        # Beat tracking
        self.beat_times = deque(maxlen=32)  # Last 16 beats
        self.beat_intervals = deque(maxlen=16)

        # Structure state
        self.current_section = "intro"
        self.section_confidence = 0.0
        self.time_in_section = 0
        self.last_section_change = time.time()

        # Drop detection
        self.drop_imminent = False
        self.drop_probability = 0.0
        self.in_drop = False
        self.drop_intensity = 0.0

        # Build-up detection
        self.in_buildup = False
        self.buildup_progress = 0.0  # 0.0 to 1.0

        # Breakdown detection
        self.in_breakdown = False
        self.breakdown_depth = 0.0  # How "deep" the breakdown is

        # Pattern recognition
        self.rhythm_pattern = "unknown"
        self.is_four_on_floor = False

        # Emotional state
        self.emotional_intensity = 0.5
        self.emotional_valence = 0.5  # negative to positive

        print("🎵 Music Structure Analyzer initialized")

    def update(self, audio_data, music_intelligence=None):
        """Update with new audio frame"""
        current_time = time.time()

        # Store histories
        self.energy_history.append(audio_data['energy'])
        self.bass_history.append(audio_data['bass'])
        self.mid_history.append(audio_data['mid'])

        # Track beats
        if audio_data['beat']:
            if len(self.beat_times) > 0:
                interval = current_time - self.beat_times[-1]
                self.beat_intervals.append(interval)
            self.beat_times.append(current_time)

        # Update time in section
        self.time_in_section = current_time - self.last_section_change

        # Analyze structure
        self._detect_buildup()
        self._detect_drop()
        self._detect_breakdown()
        self._detect_rhythm_pattern()
        self._detect_section(music_intelligence)
        self._update_emotional_state()

    def _detect_buildup(self):
        """Detect if we're in a build-up"""
        if len(self.energy_history) < 40:
            return

        # Get recent energy trends
        recent = list(self.energy_history)[-40:]  # Last 2 seconds
        older = list(self.energy_history)[-80:-40]  # 2-4 seconds ago

        recent_avg = np.mean(recent)
        older_avg = np.mean(older)

        # Calculate energy growth rate
        energy_growth = (recent_avg - older_avg) / (older_avg + 0.01)

        # Check for rising energy
        if energy_growth > 0.15:  # 15% increase
            self.in_buildup = True
            # Calculate progress (0.0 to 1.0)
            self.buildup_progress = min(1.0, energy_growth / 0.5)
        else:
            self.in_buildup = False
            self.buildup_progress = 0.0

    def _detect_drop(self):
        """Detect imminent drop and actual drop"""
        if len(self.energy_history) < 20:
            return

        recent_energy = list(self.energy_history)[-10:]
        prev_energy = list(self.energy_history)[-20:-10]

        recent_avg = np.mean(recent_energy)
        prev_avg = np.mean(prev_energy)

        # Drop imminent if build-up is strong
        if self.in_buildup and self.buildup_progress > 0.7:
            self.drop_imminent = True
            self.drop_probability = self.buildup_progress
        else:
            self.drop_imminent = False
            self.drop_probability = 0.0

        # Detect actual drop (sudden energy spike)
        energy_spike = recent_avg - prev_avg

        if energy_spike > 0.3 and recent_avg > 0.7:  # Big spike + high energy
            self.in_drop = True
            self.drop_intensity = min(1.0, energy_spike)
        else:
            # Drop lasts ~2-4 seconds
            if self.in_drop and self.time_in_section > 4.0:
                self.in_drop = False
                self.drop_intensity = 0.0

    def _detect_breakdown(self):
        """Detect breakdown (energy drop, emotional moment)"""
        if len(self.energy_history) < 20:
            return

        recent_energy = list(self.energy_history)[-10:]
        prev_energy = list(self.energy_history)[-20:-10]

        recent_avg = np.mean(recent_energy)
        prev_avg = np.mean(prev_energy)

        # Breakdown = sudden energy drop + low current energy
        energy_drop = prev_avg - recent_avg

        if energy_drop > 0.2 and recent_avg < 0.4:
            self.in_breakdown = True
            self.breakdown_depth = min(1.0, energy_drop / 0.5)
        else:
            # Breakdown can last longer
            if self.in_breakdown and self.time_in_section > 8.0:
                self.in_breakdown = False
                self.breakdown_depth = 0.0

    def _detect_rhythm_pattern(self):
        """Detect rhythm patterns (four-on-floor, etc.)"""
        if len(self.beat_intervals) < 4:
            return

        # Check beat consistency
        intervals = list(self.beat_intervals)[-8:]
        if len(intervals) < 4:
            return

        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        # Four-on-floor = very consistent beat intervals
        if std_interval < 0.05:  # Very tight timing
            self.is_four_on_floor = True
            self.rhythm_pattern = "four_on_floor"
        else:
            self.is_four_on_floor = False
            self.rhythm_pattern = "variable"

    def _detect_section(self, music_intelligence=None):
        """Detect current section (verse, chorus, etc.)"""
        # Use MusicIntelligence hints if available
        if music_intelligence:
            mi_section = music_intelligence.current_section

            # Trust MusicIntelligence but add our real-time context
            if self.in_drop:
                self.current_section = "drop"
                self.section_confidence = 0.9
            elif self.in_buildup:
                self.current_section = "buildup"
                self.section_confidence = 0.8
            elif self.in_breakdown:
                self.current_section = "breakdown"
                self.section_confidence = 0.85
            else:
                # Use MusicIntelligence section
                self.current_section = mi_section
                self.section_confidence = 0.7
        else:
            # Fallback detection
            if self.in_drop:
                self.current_section = "drop"
            elif self.in_buildup:
                self.current_section = "buildup"
            elif self.in_breakdown:
                self.current_section = "breakdown"
            else:
                self.current_section = "verse"

    def _update_emotional_state(self):
        """Update emotional intensity and valence"""
        if len(self.energy_history) < 10:
            return

        recent = list(self.energy_history)[-20:]
        bass = list(self.bass_history)[-20:]
        mid = list(self.mid_history)[-20:]

        # Intensity = overall energy level
        self.emotional_intensity = np.mean(recent)

        # Valence = balance of frequencies
        # High mid/treble = brighter, more positive
        # High bass = darker, more aggressive
        bass_avg = np.mean(bass)
        mid_avg = np.mean(mid)

        if bass_avg + mid_avg > 0:
            self.emotional_valence = mid_avg / (bass_avg + mid_avg)
        else:
            self.emotional_valence = 0.5

    def get_moment_type(self):
        """Get current moment type for AI Director"""
        if self.in_drop:
            return "drop"
        elif self.drop_imminent:
            return "pre_drop"
        elif self.in_buildup:
            return "buildup"
        elif self.in_breakdown:
            return "breakdown"
        elif self.emotional_intensity > 0.7:
            return "high_energy"
        elif self.emotional_intensity < 0.3:
            return "low_energy"
        else:
            return "normal"

    def get_urgency(self):
        """Get urgency level (0.0 to 1.0) for AI decisions"""
        if self.in_drop:
            return 1.0
        elif self.drop_imminent:
            return 0.9
        elif self.in_buildup:
            return 0.7 + (self.buildup_progress * 0.3)
        elif self.in_breakdown:
            return 0.6
        else:
            return 0.3

    def should_change_effect(self):
        """Determine if effect should change NOW"""
        # Force change on major transitions
        if self.in_drop and self.time_in_section < 0.5:
            return True, "drop_explosion"

        if self.drop_imminent and self.drop_probability > 0.85:
            return True, "pre_drop_tension"

        if self.in_breakdown and self.time_in_section < 1.0:
            return True, "breakdown_calm"

        return False, None

    def get_status_string(self):
        """Get status for debugging"""
        moment = self.get_moment_type()
        urgency = self.get_urgency()

        status = f"Section: {self.current_section} ({self.section_confidence:.2f})"
        status += f" | Moment: {moment}"
        status += f" | Urgency: {urgency:.2f}"

        if self.in_buildup:
            status += f" | Build: {self.buildup_progress:.0%}"
        if self.drop_imminent:
            status += f" | ⚠️ DROP IMMINENT ({self.drop_probability:.0%})"
        if self.in_drop:
            status += f" | 💥 DROP!"
        if self.in_breakdown:
            status += f" | 🌊 Breakdown"

        return status
