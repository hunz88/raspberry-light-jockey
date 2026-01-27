"""
AI Director - Real-time Light Show Director
Makes intelligent decisions about effects, colors, intensity in real-time
"""

import time
import random
from collections import deque


class AIDirector:
    """The intelligent director that orchestrates the entire light show"""

    def __init__(self, effect_engine):
        self.effect_engine = effect_engine
        self.effect_names = effect_engine.effect_names

        # Decision state
        self.current_strategy = "adaptive"
        self.last_decision_time = time.time()
        self.decision_history = deque(maxlen=20)

        # Moment tracking
        self.current_moment = "normal"
        self.moment_intensity = 0.5

        # Effect preferences for different moments
        self.moment_effect_map = {
            "drop": [
                "💥 Center Expand",
                "⚡ Cascade Strobe",
                "🔥 Energy Pulse",
                "🎪 Peak Time"
            ],
            "pre_drop": [
                "🌊 Invasion Wave",
                "🔄 Chase Around",
                "⚡ Strobe Zones"
            ],
            "buildup": [
                "🌊 Invasion Wave",
                "🔄 Perimeter Chase",
                "🌊 Party Wave"
            ],
            "breakdown": [
                "🚪 Welcome Flow",
                "✨ Bottle Showcase",
                "🌈 Rainbow Flow"
            ],
            "high_energy": [
                "🌊 Party Wave",
                "🔄 Chase Around",
                "🎵 Stereo Split",
                "⚡ Strobe Zones"
            ],
            "low_energy": [
                "🚪 Welcome Flow",
                "🍹 Bar Mode",
                "✨ Bottle Showcase"
            ],
            "normal": [
                "🏓 Ping Pong",
                "🔄 Perimeter Chase",
                "🎵 Stereo Split"
            ]
        }

        # Color mood mapping
        self.moment_color_mood = {
            "drop": "explosive",
            "pre_drop": "tense",
            "buildup": "rising",
            "breakdown": "calm",
            "high_energy": "vibrant",
            "low_energy": "soft",
            "normal": "balanced"
        }

        # Timing control
        self.min_effect_duration = 15  # seconds
        self.max_effect_duration = 60
        self.adaptive_duration = 30

        # Special moment flags
        self.drop_triggered = False
        self.buildup_tracked = False

        print("🎬 AI Director initialized")
        print(f"   🎯 Strategy: {self.current_strategy}")
        print(f"   🎨 Moment-aware effect selection")
        print(f"   ⚡ Real-time decision making")

    def analyze_and_decide(self, audio_data, music_structure, music_intelligence):
        """Main decision loop - called every frame"""
        current_time = time.time()

        # Get current moment
        self.current_moment = music_structure.get_moment_type()
        self.moment_intensity = music_structure.get_urgency()

        # Check for forced effect changes (drops, breakdowns)
        should_change, reason = music_structure.should_change_effect()

        if should_change:
            return self._make_urgent_decision(reason, audio_data, music_structure)

        # Check if we should change based on timing
        time_in_effect = current_time - self.effect_engine.last_effect_change

        # Adaptive duration based on moment
        if self.current_moment in ["drop", "buildup"]:
            target_duration = self.min_effect_duration
        elif self.current_moment == "breakdown":
            target_duration = self.max_effect_duration
        else:
            target_duration = self.adaptive_duration

        if time_in_effect >= target_duration:
            return self._make_transition_decision(audio_data, music_structure, music_intelligence)

        # No change needed
        return None

    def _make_urgent_decision(self, reason, audio_data, music_structure):
        """Make urgent decision for special moments"""
        print(f"\n{'🚨'*30}")
        print(f"🚨 URGENT DECISION: {reason}")

        decision = {
            "reason": reason,
            "timestamp": time.time(),
            "urgency": "critical"
        }

        if reason == "drop_explosion":
            # DROP = Maximum impact
            effect_name = random.choice([
                "💥 Center Expand",
                "⚡ Cascade Strobe",
                "🔥 Energy Pulse",
                "🎪 Peak Time"
            ])

            decision["effect"] = effect_name
            decision["intensity"] = 1.0
            decision["color_mood"] = "explosive"
            decision["special_instruction"] = "MAX_IMPACT"

            print(f"💥 DROP EXPLOSION!")
            print(f"   Effect: {effect_name}")
            print(f"   Intensity: MAXIMUM")

        elif reason == "pre_drop_tension":
            # Pre-drop = Build tension
            effect_name = random.choice([
                "🌊 Invasion Wave",
                "⚡ Strobe Zones",
                "🔄 Chase Around"
            ])

            decision["effect"] = effect_name
            decision["intensity"] = 0.9
            decision["color_mood"] = "tense"
            decision["special_instruction"] = "BUILD_TENSION"

            print(f"⚠️  PRE-DROP TENSION")
            print(f"   Effect: {effect_name}")
            print(f"   Building anticipation...")

        elif reason == "breakdown_calm":
            # Breakdown = Emotional, calm
            effect_name = random.choice([
                "🚪 Welcome Flow",
                "✨ Bottle Showcase",
                "🌈 Rainbow Flow"
            ])

            decision["effect"] = effect_name
            decision["intensity"] = 0.4
            decision["color_mood"] = "calm"
            decision["special_instruction"] = "EMOTIONAL_CALM"

            print(f"🌊 BREAKDOWN - Emotional Moment")
            print(f"   Effect: {effect_name}")
            print(f"   Creating calm atmosphere...")

        print(f"{'🚨'*30}\n")

        self.decision_history.append(decision)
        return decision

    def _make_transition_decision(self, audio_data, music_structure, music_intelligence):
        """Make decision for regular transitions"""
        current_time = time.time()

        # Get suitable effects for current moment
        suitable_effects = self.moment_effect_map.get(
            self.current_moment,
            self.moment_effect_map["normal"]
        )

        # Avoid repeating recent effects
        recent_effects = [d.get("effect") for d in list(self.decision_history)[-5:]]
        available_effects = [e for e in suitable_effects if e not in recent_effects]

        if not available_effects:
            available_effects = suitable_effects

        # Choose effect
        if music_intelligence:
            # Try to get AI recommendation
            recommended = music_intelligence.get_recommended_effect(self.effect_names)
            if recommended and recommended in available_effects:
                chosen_effect = recommended
                selection_method = "ai_recommended"
            else:
                chosen_effect = random.choice(available_effects)
                selection_method = "moment_based"
        else:
            chosen_effect = random.choice(available_effects)
            selection_method = "moment_based"

        # Determine intensity based on moment
        if self.current_moment in ["drop", "high_energy"]:
            intensity = 0.9 + (music_structure.emotional_intensity * 0.1)
        elif self.current_moment in ["breakdown", "low_energy"]:
            intensity = 0.3 + (music_structure.emotional_intensity * 0.3)
        else:
            intensity = 0.6 + (music_structure.emotional_intensity * 0.4)

        decision = {
            "reason": "adaptive_transition",
            "timestamp": current_time,
            "urgency": "normal",
            "effect": chosen_effect,
            "intensity": intensity,
            "color_mood": self.moment_color_mood.get(self.current_moment, "balanced"),
            "selection_method": selection_method
        }

        print(f"\n{'🎬'*30}")
        print(f"🎬 AI DIRECTOR DECISION")
        print(f"   Moment: {self.current_moment}")
        print(f"   Effect: {chosen_effect}")
        print(f"   Intensity: {intensity:.2f}")
        print(f"   Mood: {decision['color_mood']}")
        print(f"   Method: {selection_method}")
        print(f"{'🎬'*30}\n")

        self.decision_history.append(decision)
        return decision

    def get_dynamic_intensity(self, base_intensity, audio_data, music_structure):
        """Calculate dynamic intensity based on current moment"""
        # Start with base intensity
        intensity = base_intensity

        # Boost during drops
        if music_structure.in_drop:
            intensity = min(1.0, intensity + 0.3)

        # Boost during build-ups (progressive)
        if music_structure.in_buildup:
            boost = music_structure.buildup_progress * 0.2
            intensity = min(1.0, intensity + boost)

        # Reduce during breakdowns
        if music_structure.in_breakdown:
            intensity *= (1.0 - music_structure.breakdown_depth * 0.5)

        # Add beat pulse
        if audio_data['beat']:
            intensity = min(1.0, intensity + 0.1)

        return intensity

    def suggest_color_evolution(self, current_genre, music_structure):
        """Suggest how colors should evolve"""
        mood = self.moment_color_mood.get(self.current_moment, "balanced")

        evolution = {
            "mood": mood,
            "intensity": music_structure.emotional_intensity,
            "valence": music_structure.emotional_valence,
            "should_pulse": music_structure.in_drop or music_structure.is_four_on_floor,
            "should_fade": music_structure.in_breakdown,
            "should_strobe": music_structure.in_drop and music_structure.drop_intensity > 0.8
        }

        return evolution

    def get_status_string(self):
        """Get director status for debugging"""
        recent_decisions = list(self.decision_history)[-3:]

        status = f"Moment: {self.current_moment} ({self.moment_intensity:.2f})"

        if recent_decisions:
            last = recent_decisions[-1]
            status += f" | Last: {last.get('effect', 'N/A')} ({last.get('selection_method', 'N/A')})"

        return status
