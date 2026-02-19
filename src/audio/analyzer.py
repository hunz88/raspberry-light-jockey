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
        self.beat_timestamps = deque(maxlen=20)  # For BPM estimation
        self.estimated_bpm = 0
        
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
    
    def start(self):
        """Start audio capture and analysis"""
        if self.is_running:
            return
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device,
                frames_per_buffer=self.buffer_size,
                stream_callback=self._audio_callback
            )
            
            self.is_running = True
            
            # Start analysis thread
            self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.analysis_thread.start()
            
            print("🎤 Audio capture started")
            
        except Exception as e:
            print(f"❌ Failed to start audio: {e}")
            self.is_running = False
    
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
            'bpm': self._estimate_bpm()
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
            self.beat_timestamps.append(current_time)

        return is_beat

    def _estimate_bpm(self):
        """Estimate BPM from recent beat timestamps"""
        if len(self.beat_timestamps) < 4:
            return self.estimated_bpm  # Keep last known value

        beats = list(self.beat_timestamps)
        intervals = [beats[i] - beats[i-1] for i in range(1, len(beats))]

        avg_interval = np.mean(intervals)
        if avg_interval > 0:
            self.estimated_bpm = int(60 / avg_interval)

        return self.estimated_bpm
    
    def get_audio_features(self):
        """Get current audio features with silence detection"""
        if not hasattr(self, 'current_features'):
            return {
                'bass': 0.0,
                'mid': 0.0,
                'treble': 0.0,
                'energy': 0.0,
                'beat': False,
                'bpm': self.estimated_bpm,
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
