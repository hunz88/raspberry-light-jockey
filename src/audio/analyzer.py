"""
Audio Analyzer
Real-time audio analysis with beat detection and frequency analysis
"""

import numpy as np
import pyaudio
import threading
import time
from collections import deque
from scipy import signal


class AudioAnalyzer:
    """Real-time audio analysis"""
    
    def __init__(self, config):
        self.config = config
        
        # Audio settings
        self.sample_rate = config.get('sample_rate', 44100)
        self.buffer_size = config.get('buffer_size', 2048)
        self.channels = config.get('channels', 1)
        self.input_device = config.get('input_device', None)
        
        # Beat detection
        self.beat_sensitivity = config.get('beat_sensitivity', 0.5)
        self.energy_history = deque(maxlen=43)  # ~1 second at 44100/1024
        self.last_beat_time = 0
        self.min_beat_interval = 0.2  # Minimum 200ms between beats
        
        # Frequency ranges
        freq_ranges = config.get('frequency_ranges', {})
        self.bass_range = freq_ranges.get('bass', [20, 250])
        self.mid_range = freq_ranges.get('mid', [250, 4000])
        self.treble_range = freq_ranges.get('treble', [4000, 20000])
        
        # PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # State
        self.is_running = False
        self.current_features = {
            'bass': 0.0,
            'mid': 0.0,
            'treble': 0.0,
            'energy': 0.0,
            'beat': False,
            'bpm': 0
        }
        
        # Thread
        self.analysis_thread = None
        
        # Audio buffer
        self.audio_buffer = deque(maxlen=int(self.sample_rate * 10))  # 10 seconds
        
        print(f"🎤 Audio analyzer initialized")
        print(f"   Sample rate: {self.sample_rate} Hz")
        print(f"   Buffer size: {self.buffer_size}")
        print(f"   Device: {self.input_device if self.input_device else 'default'}")
    
    def _try_open_stream(self, device_index, channels):
        """Try to open a stream with given device and channel count. Returns stream or None."""
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.buffer_size,
                stream_callback=self._audio_callback
            )
            return stream, channels
        except Exception:
            return None, channels

    def _find_working_input(self):
        """Auto-discover a working input device + channel count."""
        n = self.audio.get_device_count()
        print(f"🔍 Scanning {n} audio devices...")

        candidates = []

        # Prefer configured device first
        if self.input_device is not None:
            candidates.append(self.input_device)

        # Then all devices with at least 1 input channel
        for i in range(n):
            try:
                info = self.audio.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0 and i not in candidates:
                    candidates.append(i)
            except Exception:
                pass

        for dev_idx in candidates:
            try:
                info = self.audio.get_device_info_by_index(dev_idx)
                name = info.get('name', '?')
                max_ch = int(info.get('maxInputChannels', 0))
                if max_ch == 0:
                    continue

                # Try channels in order: configured, 1, 2
                for ch in sorted({self.channels, 1, min(2, max_ch)}, key=lambda x: abs(x - self.channels)):
                    if ch < 1 or ch > max_ch:
                        continue
                    stream, used_ch = self._try_open_stream(dev_idx, ch)
                    if stream:
                        print(f"   ✅ Device [{dev_idx}] '{name}' — {used_ch}ch @ {self.sample_rate}Hz")
                        self.channels = used_ch
                        self.input_device = dev_idx
                        return stream

                print(f"   ⛔ Device [{dev_idx}] '{name}' — no working config")
            except Exception:
                pass

        return None

    def start(self):
        """Start audio capture and analysis"""
        if self.is_running:
            return

        # First try the configured device/channels directly
        stream = None
        if self.input_device is not None:
            stream, _ = self._try_open_stream(self.input_device, self.channels)
            if stream:
                print(f"🎤 Using configured device [{self.input_device}] — {self.channels}ch")

        # Auto-discover if configured device failed
        if stream is None:
            print("⚠️  Configured audio device failed, auto-discovering...")
            stream = self._find_working_input()

        if stream is None:
            print("❌ No working audio input found. Running without audio reactivity.")
            self.is_running = False
            return

        self.stream = stream
        self.is_running = True

        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()

        print("🎤 Audio capture started")
    
    def stop(self):
        """Stop audio capture"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1.0)
        
        print("🎤 Audio capture stopped")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback"""
        if status:
            print(f"⚠️  Audio status: {status}")
        
        # Convert to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Store in buffer
        self.audio_buffer.extend(audio_data)
        
        return (in_data, pyaudio.paContinue)
    
    def _analysis_loop(self):
        """Main analysis loop"""
        print("🔄 Analysis loop started")
        
        while self.is_running:
            try:
                if len(self.audio_buffer) < self.buffer_size:
                    time.sleep(0.01)
                    continue
                
                # Get latest buffer
                audio_data = np.array(list(self.audio_buffer)[-self.buffer_size:])
                
                # Analyze
                features = self._analyze_audio(audio_data)
                
                # Update current features
                self.current_features = features
                
                # Small delay
                time.sleep(0.02)  # ~50Hz update rate
                
            except Exception as e:
                print(f"❌ Analysis error: {e}")
                time.sleep(0.1)
    
    def _analyze_audio(self, audio_data):
        """Analyze audio buffer"""
        # Normalize
        audio_data = audio_data.astype(np.float32) / 32768.0
        
        # FFT
        fft = np.fft.rfft(audio_data)
        fft_magnitude = np.abs(fft)
        fft_freq = np.fft.rfftfreq(len(audio_data), 1.0 / self.sample_rate)
        
        # Frequency bands
        bass = self._get_band_energy(fft_magnitude, fft_freq, self.bass_range)
        mid = self._get_band_energy(fft_magnitude, fft_freq, self.mid_range)
        treble = self._get_band_energy(fft_magnitude, fft_freq, self.treble_range)
        
        # Total energy
        energy = np.mean(np.abs(audio_data))
        
        # Beat detection
        beat = self._detect_beat(energy)
        
        # Normalize values
        features = {
            'bass': min(1.0, bass),
            'mid': min(1.0, mid),
            'treble': min(1.0, treble),
            'energy': min(1.0, energy * 10),  # Scale up
            'beat': beat,
            'bpm': 0  # TODO: BPM detection
        }
        
        return features
    
    def _get_band_energy(self, fft_magnitude, fft_freq, freq_range):
        """Get energy in frequency band"""
        mask = (fft_freq >= freq_range[0]) & (fft_freq <= freq_range[1])
        band_energy = np.mean(fft_magnitude[mask]) if np.any(mask) else 0.0
        return band_energy
    
    def _detect_beat(self, energy):
        """Simple beat detection"""
        self.energy_history.append(energy)
        
        if len(self.energy_history) < 10:
            return False
        
        # Check if current energy is significantly higher than average
        avg_energy = np.mean(self.energy_history)
        threshold = avg_energy * (1.0 + self.beat_sensitivity)
        
        current_time = time.time()
        is_beat = (
            energy > threshold and
            (current_time - self.last_beat_time) > self.min_beat_interval
        )
        
        if is_beat:
            self.last_beat_time = current_time
        
        return is_beat
    
    def get_audio_features(self):
        """Get current audio features with silence detection"""
        if not hasattr(self, 'current_features'):
            return {
                'bass': 0.0,
                'mid': 0.0,
                'treble': 0.0,
                'energy': 0.0,
                'beat': False,
                'bpm': 0,
                'is_silent': True
            }
        
        features = self.current_features.copy()
        
        # Add silence detection
        features['is_silent'] = features.get('energy', 0) < 0.05
        
        return features
    
    def get_raw_audio(self, duration=5.0):
        """Get raw audio buffer for song recognition"""
        if not self.is_running:
            return None
        
        # Calculate samples needed
        samples_needed = int(self.sample_rate * duration)
        
        if len(self.audio_buffer) < samples_needed:
            return None
        
        # Get last N seconds
        audio_data = np.array(list(self.audio_buffer)[-samples_needed:])
        
        return audio_data
    
    def __del__(self):
        """Cleanup"""
        self.stop()
        if hasattr(self, 'audio'):
            self.audio.terminate()
