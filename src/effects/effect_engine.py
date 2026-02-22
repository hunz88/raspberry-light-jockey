"""
Effect Engine with Music Intelligence + Dynamic Colors
"""

import asyncio
import time
import random
import colorsys
import math


class EffectEngine:
    """Effect engine with MUSIC INTELLIGENCE + DYNAMIC COLORS"""
    
    def __init__(self, wiz_controller, audio_analyzer, config):
        self.wiz_controller = wiz_controller
        self.audio_analyzer = audio_analyzer
        self.config = config
        
        # MUSIC INTELLIGENCE
        from audio.music_intelligence import MusicIntelligence
        self.music_intelligence = MusicIntelligence()
        
        # DYNAMIC COLOR SYSTEM
        from effects.color_system import ColorSystem
        self.color_system = ColorSystem()
        
        # Effect settings
        self.current_effect = 0
        self.effect_duration = config.get('effect_duration', 45)
        self.last_effect_change = time.time()
        self.last_debug_time = 0
        
        # Song recognition
        self.shazam_client = None
        self.current_song_name = None
        self.suggested_effect_idx = None
        
        # Effect state
        self.is_running = False
        self.effect_loop_task = None
        
        # Animation state
        self.wave_position = 0
        self.rainbow_offset = 0
        self.chase_position = 0
        self.strobe_state = 0
        
        # Zone definitions
        self.zones = {
            'dj': list(range(0, 5)),
            'corridor': [5],
            'salon_left': [6, 7, 8, 9],
            'salon_right': [10, 11, 12, 13],
            'salon_back': [14],
            'bar_top': list(range(15, 19)),
            'bar_floor_left': list(range(19, 23)),
            'bar_floor_right': list(range(23, 27)),
            'strips': list(range(27, 30)),
            'extra': [30]
        }
        
        self.zones['salon'] = self.zones['salon_left'] + self.zones['salon_right'] + self.zones['salon_back']
        self.zones['bar_floor'] = self.zones['bar_floor_left'] + self.zones['bar_floor_right']
        self.zones['bar'] = self.zones['bar_top'] + self.zones['bar_floor']
        
        # Effects
        self.effects = [
            self.effect_invasion_wave,
            self.effect_perimeter_chase,
            self.effect_ping_pong,
            self.effect_center_expand,
            self.effect_cascade_strobe,
            self.effect_welcome_flow,
            self.effect_bar_mode,
            self.effect_party_wave,
            self.effect_stereo_split,
            self.effect_chase_around,
            self.effect_strobe_zones,
            self.effect_bottle_showcase,
            self.effect_energy_pulse,
            self.effect_rainbow_flow,
            self.effect_peak_time
        ]
        
        self.effect_names = [
            "🌊 Invasion Wave",
            "🔄 Perimeter Chase",
            "🏓 Ping Pong",
            "💥 Center Expand",
            "⚡ Cascade Strobe",
            "🚪 Welcome Flow",
            "🍹 Bar Mode",
            "🌊 Party Wave",
            "🎵 Stereo Split",
            "🔄 Chase Around",
            "⚡ Strobe Zones",
            "✨ Bottle Showcase",
            "🔥 Energy Pulse",
            "🌈 Rainbow Flow",
            "🎪 Peak Time"
        ]
        
        print("⚡ Effect Engine + Intelligence + Colors")
        print(f"   🎨 Effects: {len(self.effects)}")
    
    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.effect_loop_task = asyncio.create_task(self._effect_loop())
        print("⚡ Started")
    
    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.effect_loop_task:
            self.effect_loop_task.cancel()
            try:
                await self.effect_loop_task
            except asyncio.CancelledError:
                pass
        await self.wiz_controller.turn_off()
    
    async def _effect_loop(self):
        print(f"\n🎬 MUSIC INTELLIGENCE + DYNAMIC COLORS Active!\n")
        
        last_song_check = 0
        
        while self.is_running:
            try:
                audio_data = self.audio_analyzer.get_audio_features()
                current_time = time.time()
                time_in_effect = current_time - self.last_effect_change
                
                # Update Intelligence
                self.music_intelligence.update(audio_data)
                
                # Update Color System
                self.color_system.set_emotion(self.music_intelligence.current_emotion)
                
                # Shazam check
                if current_time - last_song_check > 30:
                    last_song_check = current_time
                    asyncio.create_task(self._check_song_and_suggest())
                
                # Debug
                if current_time - self.last_debug_time >= 10.0:
                    self.last_debug_time = current_time
                    silent = audio_data.get('is_silent', False)
                    status = "🔇 SILENT" if silent else "🔊 PLAYING"
                    
                    print(f"\n{'='*60}")
                    print(f"🎨 {self.effect_names[self.current_effect]}")
                    print(f"⏱️  {int(time_in_effect)}s / {self.effect_duration}s")
                    print(f"📊 Bass={audio_data['bass']:.2f} Energy={audio_data['energy']:.2f}")
                    print(f"🎵 {status}")
                    print(f"🧠 {self.music_intelligence.get_status_string()}")
                    if self.current_song_name:
                        print(f"🎼 {self.current_song_name}")
                    print(f"{'='*60}\n")
                
                # Silence
                if audio_data.get('is_silent', False):
                    await self.set_zone('salon', 30, 30, 60, 40)
                    await self.set_zone('dj', 40, 40, 70, 50)
                    await self.set_zone('bar', 60, 60, 90, 60)
                    await self.set_zone('strips', 100, 50, 0, 80)
                    await asyncio.sleep(0.2)
                    continue
                
                # INTELLIGENT CHANGE
                if time_in_effect > self.effect_duration:
                    recommended = self.music_intelligence.get_recommended_effect(self.effect_names)
                    
                    if recommended and recommended in self.effect_names:
                        old = self.effect_names[self.current_effect]
                        self.current_effect = self.effect_names.index(recommended)
                        self.last_effect_change = current_time
                        
                        print(f"\n{'🧠'*30}")
                        print(f"🧠 INTELLIGENT CHANGE 🧠")
                        print(f"📤 {old}")
                        print(f"📥 {recommended}")
                        print(f"🎯 {self.music_intelligence.current_section} / {self.music_intelligence.current_emotion}")
                        print(f"{'🧠'*30}\n")
                        
                    else:
                        # Fallback: always rotate after timeout.
                        # Prefer a beat boundary for a musical transition, but
                        # force the change if we've already waited an extra 5 s.
                        overtime = time_in_effect - self.effect_duration
                        if audio_data['beat'] or audio_data['energy'] < 0.3 or overtime > 5:
                            old = self.effect_names[self.current_effect]

                            if self.suggested_effect_idx is not None:
                                self.current_effect = self.suggested_effect_idx
                                self.suggested_effect_idx = None
                            else:
                                self.current_effect = (self.current_effect + 1) % len(self.effects)

                            new = self.effect_names[self.current_effect]
                            self.last_effect_change = current_time

                            print(f"\n{'🌟'*30}")
                            print(f"✨ SMART CHANGE ✨")
                            print(f"📤 {old} → 📥 {new}")
                            print(f"{'🌟'*30}\n")
                
                await self.effects[self.current_effect](audio_data)
                await asyncio.sleep(0.05)
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                await asyncio.sleep(0.1)
    
    async def _check_song_and_suggest(self):
        try:
            print("\n🎵 Checking song...")
            audio_data = self.audio_analyzer.get_raw_audio(duration=8.0)
            if audio_data is None:
                return
            
            if self.shazam_client:
                song_info = await self.shazam_client.recognize_song(audio_data, self.audio_analyzer.sample_rate)
                
                if song_info:
                    title = song_info.get('title', 'Unknown')
                    artist = song_info.get('artist', 'Unknown')
                    genre = song_info.get('genre', 'Unknown')
                    
                    self.current_song_name = f"{artist} - {title}"
                    self.music_intelligence.set_song_metadata(genre)
                    
                    # UPDATE COLOR SYSTEM
                    self.color_system.set_genre(genre)
                    
                    print(f"   ✅ {self.current_song_name}")
                    print(f"   🎸 {genre}")
        except Exception as e:
            print(f"   ❌ {e}")
    
    async def set_zone(self, zone_name, r, g, b, brightness=200):
        if zone_name not in self.zones:
            return
        tasks = []
        for idx in self.zones[zone_name]:
            if idx < len(self.wiz_controller.lights):
                light = self.wiz_controller.lights[idx]
                tasks.append(self._set_light(light, r, g, b, brightness))
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _set_light(self, light, r, g, b, brightness):
        try:
            from pywizlight import PilotBuilder
            # Clamp all channels to the valid [0, 255] range.
            r = max(0, min(255, int(r)))
            g = max(0, min(255, int(g)))
            b = max(0, min(255, int(b)))
            brightness = max(0, min(255, int(brightness)))
            pilot = PilotBuilder(rgb=(r, g, b), brightness=brightness)
            await light.turn_on(pilot)
        except:
            pass
    
    def hsv_to_rgb(self, h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)
    
    # ========================================
    # EFFECTS WITH DYNAMIC COLORS + MOVEMENT
    # ========================================
    
    async def effect_invasion_wave(self, audio_data):
        """🌊 Wave from DJ to Salon with GENRE COLORS"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            self.wave_position += int(4 * intensity)
        else:
            self.wave_position += int(2 * intensity)
        
        path = self.zones['dj'] + self.zones['corridor'] + self.zones['salon']
        
        tasks = []
        for idx in range(len(self.wiz_controller.lights)):
            if idx in path:
                pos = path.index(idx)
                distance = abs(pos - (self.wave_position % len(path)))
                
                if distance < 5:
                    brightness = int((255 - (distance * 40)) * intensity)
                    # PRIMARY COLOR from genre
                    r, g, b = self.color_system.get_primary_color(intensity)
                else:
                    brightness = 50
                    r, g, b = self.color_system.get_secondary_color(0.3)
                
                light = self.wiz_controller.lights[idx]
                tasks.append(self._set_light(light, r, g, b, brightness))
            else:
                # Bar: COMPLEMENTARY COLOR
                light = self.wiz_controller.lights[idx]
                r, g, b = self.color_system.get_complementary(intensity)
                tasks.append(self._set_light(light, r, g, b, int(150 * intensity)))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_perimeter_chase(self, audio_data):
        """🔄 Chase with GRADIENT COLORS"""
        beat = audio_data['beat']
        energy = audio_data['energy']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            self.chase_position += int(3 * intensity)
        else:
            self.chase_position += int(1 * intensity)
        
        perimeter = [0, 1] + [5] + self.zones['salon_left'] + [14] + list(reversed(self.zones['salon_right'])) + [3, 4]
        
        tasks = []
        for idx in range(len(self.wiz_controller.lights)):
            light = self.wiz_controller.lights[idx]
            
            if idx in perimeter:
                pos = perimeter.index(idx)
                chase_offset = (self.chase_position - pos) % len(perimeter)
                
                if chase_offset < 5:
                    brightness = int((255 - (chase_offset * 45)) * intensity)
                    # GRADIENT color based on position in chase
                    gradient_pos = chase_offset / 10
                    r, g, b = self.color_system.get_gradient_color(gradient_pos, intensity)
                    tasks.append(self._set_light(light, r, g, b, brightness))
                else:
                    tasks.append(self._set_light(light, 0, 0, 30, 30))
            else:
                # Bar: ACCENT COLOR pulsing
                bar_brightness = int((100 + energy * 155) * intensity)
                r, g, b = self.color_system.get_accent_color(intensity)
                tasks.append(self._set_light(light, r, g, b, bar_brightness))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_ping_pong(self, audio_data):
        """🏓 Ping Pong with PRIMARY/SECONDARY alternating"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        speed = 0.5 if beat else 0.2
        self.wave_position += speed * intensity
        progress = (math.sin(self.wave_position) + 1) / 2
        
        path = self.zones['dj'] + self.zones['corridor'] + self.zones['salon']
        wave_pos = int(progress * len(path))
        
        tasks = []
        for idx in range(len(self.wiz_controller.lights)):
            light = self.wiz_controller.lights[idx]
            
            if idx in path:
                pos = path.index(idx)
                distance = abs(pos - wave_pos)
                
                if distance < 4:
                    brightness = int((255 - (distance * 50)) * intensity)
                    # Alternate PRIMARY/SECONDARY
                    if progress > 0.5:
                        r, g, b = self.color_system.get_primary_color(intensity)
                    else:
                        r, g, b = self.color_system.get_secondary_color(intensity)
                else:
                    brightness = 40
                    r, g, b = self.color_system.get_accent_color(0.2)
                
                tasks.append(self._set_light(light, r, g, b, brightness))
            else:
                # Bar follows wave
                bar_brightness = int((80 + progress * 175) * intensity)
                r, g, b = self.color_system.get_complementary(intensity)
                tasks.append(self._set_light(light, r, g, b, bar_brightness))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_center_expand(self, audio_data):
        """💥 Explosion with DYNAMIC COLORS"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat or self.music_intelligence.current_section == "drop":
            self.wave_position = 0
        else:
            self.wave_position += intensity
        
        distances = {}
        for idx in range(len(self.wiz_controller.lights)):
            if idx in self.zones['dj']:
                distances[idx] = 0
            elif idx in self.zones['corridor']:
                distances[idx] = 1
            elif idx in self.zones['salon']:
                distances[idx] = 2
            elif idx in self.zones['bar']:
                distances[idx] = 3
            else:
                distances[idx] = 4
        
        tasks = []
        for idx, dist in distances.items():
            light = self.wiz_controller.lights[idx]
            wave_distance = self.wave_position / 10
            
            if abs(dist - wave_distance) < 0.8:
                brightness = int(255 * intensity)
                # PRIMARY at wave front
                r, g, b = self.color_system.get_primary_color(intensity)
            elif dist < wave_distance:
                fade = 1.0 - min(1.0, (wave_distance - dist) / 2)
                brightness = int(100 * fade * intensity)
                # SECONDARY in wake
                r, g, b = self.color_system.get_secondary_color(fade)
            else:
                brightness = 30
                r, g, b = 10, 10, 30
            
            tasks.append(self._set_light(light, r, g, b, brightness))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_cascade_strobe(self, audio_data):
        """⚡ Strobe cascade with WHITE + ACCENT"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        self.strobe_state = (self.strobe_state + int(1 * intensity)) % 31
        
        tasks = []
        for idx in range(len(self.wiz_controller.lights)):
            light = self.wiz_controller.lights[idx]
            offset = (self.strobe_state - idx) % 31
            
            if offset == 0:
                # White flash
                tasks.append(self._set_light(light, 255, 255, 255, int(255 * intensity)))
            elif offset < 3:
                # Colored trail
                brightness = int((150 - (offset * 50)) * intensity)
                r, g, b = self.color_system.get_accent_color(intensity)
                tasks.append(self._set_light(light, r, g, b, brightness))
            else:
                tasks.append(self._set_light(light, 0, 0, 20, 20))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        if not beat:
            await asyncio.sleep(0.05)
    
    async def effect_welcome_flow(self, audio_data):
        """🚪 Welcome with GRADIENT"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        # DJ: Primary pulsing
        brightness = int((150 + audio_data['bass'] * 105) * intensity)
        r, g, b = self.color_system.get_primary_color(intensity)
        await self.set_zone('dj', r, g, b, brightness)
        
        # Corridor: Secondary wave
        wave = math.sin(time.time() * 2) * 0.5 + 0.5
        brightness = int((100 + wave * 155) * intensity)
        r, g, b = self.color_system.get_secondary_color(intensity)
        await self.set_zone('corridor', r, g, b, brightness)
        
        # Salon: Accent
        brightness = int((120 + audio_data['energy'] * 135) * intensity)
        r, g, b = self.color_system.get_accent_color(intensity)
        await self.set_zone('salon', r, g, b, brightness)
        
        # Bar & Strips: Complementary
        r, g, b = self.color_system.get_complementary(0.5)
        await self.set_zone('bar', r, g, b, 80)
        r, g, b = self.color_system.get_primary_color(1.0)
        await self.set_zone('strips', r, g, b, 200)
    
    async def effect_bar_mode(self, audio_data):
        """🍹 Bar focus with WARM colors"""
        intensity = self.music_intelligence.get_effect_intensity()
        
        # Bar bright with primary
        r, g, b = self.color_system.get_primary_color(1.0)
        await self.set_zone('bar_top', r, g, b, int(255 * intensity))
        
        r, g, b = self.color_system.get_secondary_color(1.0)
        await self.set_zone('bar_floor', r, g, b, int(220 * intensity))
        
        # Strips animated
        for i, idx in enumerate(self.zones['strips']):
            gradient_pos = (time.time() / 5 + i / 3) % 1.0
            r, g, b = self.color_system.get_gradient_color(gradient_pos, 1.0)
            if idx < len(self.wiz_controller.lights):
                await self._set_light(self.wiz_controller.lights[idx], r, g, b, int(255 * intensity))
        
        # Salon dim
        r, g, b = self.color_system.get_complementary(0.5)
        brightness = int((60 + audio_data['energy'] * 60) * intensity)
        await self.set_zone('salon', r, g, b, brightness)
    
    async def effect_party_wave(self, audio_data):
        """🌊 Party wave with MOVING GRADIENT"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            self.wave_position += int(3 * intensity)
        else:
            self.wave_position += int(1 * intensity)
        
        tasks = []
        num_lights = len(self.wiz_controller.lights)
        
        for i, light in enumerate(self.wiz_controller.lights):
            wave_offset = (self.wave_position + i * 2) % num_lights
            wave_val = math.sin(wave_offset / 5) * 0.5 + 0.5
            brightness = int((100 + wave_val * 155) * intensity)
            
            # Gradient based on position
            gradient_pos = (i / num_lights + self.wave_position / 100) % 1.0
            r, g, b = self.color_system.get_gradient_color(gradient_pos, intensity)
            
            tasks.append(self._set_light(light, r, g, b, brightness))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_stereo_split(self, audio_data):
        """🎵 Left/Right with PRIMARY/SECONDARY"""
        bass = audio_data['bass']
        mid = audio_data['mid']
        intensity = self.music_intelligence.get_effect_intensity()
        
        # Left: Primary
        left_brightness = int((150 + bass * 105) * intensity)
        r, g, b = self.color_system.get_primary_color(intensity)
        await self.set_zone('salon_left', r, g, b, left_brightness)
        await self.set_zone('bar_floor_left', r, g, b, left_brightness)
        
        # Right: Secondary
        right_brightness = int((150 + mid * 105) * intensity)
        r, g, b = self.color_system.get_secondary_color(intensity)
        await self.set_zone('salon_right', r, g, b, right_brightness)
        await self.set_zone('bar_floor_right', r, g, b, right_brightness)
        
        # DJ: Accent
        r, g, b = self.color_system.get_accent_color(intensity)
        await self.set_zone('dj', r, g, b, int(150 * intensity))
        
        # Bar/Strips: Complementary
        r, g, b = self.color_system.get_complementary(1.0)
        await self.set_zone('bar_top', r, g, b, 200)
        await self.set_zone('strips', r, g, b, 255)
    
    async def effect_chase_around(self, audio_data):
        """🔄 Chase with GRADIENT trail"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            self.chase_position += int(2 * intensity)
        else:
            self.chase_position += int(1 * intensity)
        
        path = self.zones['dj'] + self.zones['corridor'] + self.zones['salon_left'] + self.zones['salon_back'] + self.zones['salon_right']
        
        tasks = []
        for i in range(len(self.wiz_controller.lights)):
            light = self.wiz_controller.lights[i]
            
            if i in path:
                pos_in_path = path.index(i)
                chase_offset = (self.chase_position - pos_in_path) % len(path)
                
                if chase_offset < 3:
                    brightness = int((255 - (chase_offset * 80)) * intensity)
                    gradient_pos = chase_offset / 10
                    r, g, b = self.color_system.get_gradient_color(gradient_pos, intensity)
                    tasks.append(self._set_light(light, r, g, b, brightness))
                else:
                    tasks.append(self._set_light(light, 0, 0, 0, 0))
            else:
                r, g, b = self.color_system.get_complementary(0.7)
                tasks.append(self._set_light(light, r, g, b, int(150 * intensity)))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_strobe_zones(self, audio_data):
        """⚡ Zone strobes with COLORS"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            self.strobe_state = (self.strobe_state + 1) % 3
        
        if self.strobe_state == 0:
            r, g, b = self.color_system.get_primary_color(1.0)
            await self.set_zone('dj', r, g, b, int(255 * intensity))
            await self.set_zone('corridor', r, g, b, int(255 * intensity))
            await self.set_zone('salon', 0, 0, 0, 0)
            await self.set_zone('bar', 0, 0, 0, 0)
        elif self.strobe_state == 1:
            r, g, b = self.color_system.get_secondary_color(1.0)
            await self.set_zone('salon', r, g, b, int(255 * intensity))
            await self.set_zone('dj', 0, 0, 0, 0)
            await self.set_zone('bar', 0, 0, 0, 0)
        else:
            r, g, b = self.color_system.get_accent_color(1.0)
            await self.set_zone('bar', r, g, b, int(255 * intensity))
            await self.set_zone('dj', 0, 0, 0, 0)
            await self.set_zone('salon', 0, 0, 0, 0)
        
        r, g, b = self.color_system.get_complementary(1.0)
        await self.set_zone('strips', r, g, b, 255)
    
    async def effect_bottle_showcase(self, audio_data):
        """✨ Bottle showcase with RAINBOW from palette"""
        energy = audio_data['energy']
        intensity = self.music_intelligence.get_effect_intensity()
        
        # Strips: Gradient animation
        for i, idx in enumerate(self.zones['strips']):
            gradient_pos = (time.time() / 5 + i / 3) % 1.0
            r, g, b = self.color_system.get_gradient_color(gradient_pos, 1.0)
            if idx < len(self.wiz_controller.lights):
                await self._set_light(self.wiz_controller.lights[idx], r, g, b, int(255 * intensity))
        
        # Main zones: Primary color
        r, g, b = self.color_system.get_primary_color(intensity)
        brightness = int((120 + energy * 135) * intensity)
        
        await self.set_zone('dj', r, g, b, brightness)
        await self.set_zone('salon', r, g, b, brightness)
        await self.set_zone('bar', r, g, b, brightness)
    
    async def effect_energy_pulse(self, audio_data):
        """🔥 All pulse with PRIMARY"""
        beat = audio_data['beat']
        energy = audio_data['energy']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            brightness = int(255 * intensity)
        else:
            brightness = int((80 + energy * 175) * intensity)
        
        r, g, b = self.color_system.get_primary_color(intensity)
        
        tasks = []
        for light in self.wiz_controller.lights:
            tasks.append(self._set_light(light, r, g, b, brightness))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_rainbow_flow(self, audio_data):
        """🌈 Rainbow from genre palette"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            self.rainbow_offset += int(5 * intensity)
        else:
            self.rainbow_offset += int(1 * intensity)
        
        tasks = []
        num_lights = len(self.wiz_controller.lights)
        
        for i, light in enumerate(self.wiz_controller.lights):
            gradient_pos = ((i / num_lights) + (self.rainbow_offset / 100)) % 1.0
            r, g, b = self.color_system.get_gradient_color(gradient_pos, intensity)
            brightness = int((150 + audio_data['energy'] * 105) * intensity)
            
            tasks.append(self._set_light(light, r, g, b, brightness))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def effect_peak_time(self, audio_data):
        """🎪 Chaos with PALETTE colors"""
        beat = audio_data['beat']
        intensity = self.music_intelligence.get_effect_intensity()
        
        if beat:
            tasks = []
            for light in self.wiz_controller.lights:
                # Random color from palette
                gradient_pos = random.random()
                r, g, b = self.color_system.get_gradient_color(gradient_pos, intensity)
                brightness = int(random.randint(200, 255) * intensity)
                tasks.append(self._set_light(light, r, g, b, brightness))
            
            await asyncio.gather(*tasks, return_exceptions=True)
