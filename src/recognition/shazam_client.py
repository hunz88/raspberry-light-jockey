"""
Shazam Client
Song recognition using ShazamIO (free and unlimited)
"""

import asyncio
from shazamio import Shazam
import numpy as np
import wave
import os


class ShazamClient:
    """Shazam song recognition client"""
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.get('enabled', True)
        
        # Initialize ShazamIO
        self.shazam = Shazam()
        
        print("🎵 ShazamIO client initialized (FREE & UNLIMITED!)")
    
    async def recognize_song(self, audio_data, sample_rate=44100):
        """Recognize song from audio data"""
        if not self.enabled:
            return None
        
        try:
            print("🔍 Recognizing song with Shazam...")
            
            # Convert to proper WAV file
            wav_path = '/tmp/shazam_sample.wav'
            self._save_wav(audio_data, sample_rate, wav_path)
            
            # Recognize using file path
            result = None
            
            if hasattr(self.shazam, 'recognize_song'):
                result = await self.shazam.recognize_song(wav_path)
            elif hasattr(self.shazam, 'recognize'):
                result = await self.shazam.recognize(wav_path)
            else:
                print("   ⚠️  ShazamIO method not found")
                return None
            
            # Cleanup temp file
            try:
                os.remove(wav_path)
            except:
                pass
            
            # Parse result
            if result and 'track' in result:
                track = result['track']
                
                bpm = self._extract_bpm(track)
                song_info = {
                    'title': track.get('title', 'Unknown'),
                    'artist': track.get('subtitle', 'Unknown Artist'),
                    'genre': self._extract_genre(track),
                    'bpm': bpm,
                    'shazam_url': track.get('url', ''),
                    'cover_art': track.get('images', {}).get('coverart', ''),
                }

                print(f"   ✅ Found: {song_info['artist']} - {song_info['title']}")
                print(f"   🎸 Genre: {song_info['genre']}")
                if bpm:
                    print(f"   🥁 BPM: {bpm}")
                
                return song_info
            else:
                print("   ❓ No match found")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def _save_wav(self, audio_data, sample_rate, filepath):
        """Save audio data as WAV file"""
        # Ensure int16
        if audio_data.dtype != np.int16:
            audio_data = (audio_data * 32767).astype(np.int16)
        
        # Write WAV file
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
    
    def _extract_bpm(self, track):
        """Extract BPM from Shazam track metadata"""
        try:
            if 'sections' in track:
                for section in track['sections']:
                    if section.get('type') == 'SONG':
                        for item in section.get('metadata', []):
                            if item.get('title') in ('BPM', 'Tempo'):
                                val = item.get('text', '').strip()
                                if val.isdigit():
                                    return int(val)
        except Exception:
            pass
        return None

    def _extract_genre(self, track):
        """Extract genre from track data"""
        try:
            # Try primary genre
            if 'genres' in track and 'primary' in track['genres']:
                return track['genres']['primary']
            
            # Try metadata
            if 'sections' in track:
                for section in track['sections']:
                    if section.get('type') == 'SONG':
                        metadata = section.get('metadata', [])
                        for item in metadata:
                            if item.get('title') == 'Genre':
                                return item.get('text', 'Unknown')
            
            return 'Unknown'
            
        except Exception:
            return 'Unknown'


# Test function
async def test_shazam():
    """Test Shazam client"""
    print("🧪 Testing Shazam client...")
    
    from shazamio import Shazam
    s = Shazam()
    
    # Check methods
    print("\n📋 Available Shazam methods:")
    if hasattr(s, 'recognize_song'):
        print("   ✅ recognize_song")
    if hasattr(s, 'recognize'):
        print("   ✅ recognize")
    
    methods = [m for m in dir(s) if 'recog' in m.lower() and not m.startswith('_')]
    print(f"   All methods: {methods}")


if __name__ == '__main__':
    asyncio.run(test_shazam())
