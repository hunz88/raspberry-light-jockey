#!/usr/bin/env python3
"""
Raspberry Pi Light Jockey - HYBRID System
Song Recognition + Audio Reactive
"""

import asyncio
import yaml
import sys
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from audio.analyzer import AudioAnalyzer
from lights.wiz_controller import WizController
from effects.effect_engine import EffectEngine
from recognition.shazam_client import ShazamClient


class LightJockey:
    """Main HYBRID application"""
    
    def __init__(self, config_path='config/config.yaml'):
        print("=" * 60)
        print("🎵 Light Jockey HYBRID - Starting...")
        print("=" * 60)
        
        self.config = self._load_config(config_path)
        
        self.audio_analyzer = None
        self.wiz_controller = None
        self.effect_engine = None
        self.shazam_client = None
        self.ai_suggester = None

        self.is_running = False
        
        print("\n🎵 Initializing audio analyzer...")
        audio_config = self.config.get('audio', {})
        self.audio_analyzer = AudioAnalyzer(audio_config)
        
        print("\n🎼 Initializing Shazam...")
        recognition_config = self.config.get('recognition', {})
        self.shazam_client = ShazamClient(recognition_config)

        print("\n🤖 Initializing AI provider...")
        self.ai_suggester = self._init_ai_provider()

        print("✅ Light Jockey initialized!")
        print("=" * 60)
    
    def _init_ai_provider(self):
        """Initialize AI provider from config"""
        ai_config = self.config.get('ai', {})
        provider = ai_config.get('provider', 'gemini')

        try:
            if provider == 'ollama':
                from ai.ollama_suggester import OllamaColorSuggester
                cfg = ai_config.get('ollama', {})
                return OllamaColorSuggester(
                    host=cfg.get('host', 'http://localhost:11434'),
                    model=cfg.get('model', 'llama3:8b')
                )
            elif provider == 'gemini':
                from ai.gemini_suggester import GeminiColorSuggester
                cfg = ai_config.get('gemini', {})
                return GeminiColorSuggester(
                    api_key=cfg.get('api_key', ''),
                    model=cfg.get('model', 'gemini-pro')
                )
            elif provider == 'claude':
                from ai.claude_suggester import ClaudeColorSuggester
                cfg = ai_config.get('claude', {})
                return ClaudeColorSuggester(
                    api_key=cfg.get('api_key', ''),
                    model=cfg.get('model', 'claude-sonnet-4-20250514')
                )
            else:
                print(f"⚠️  Provider AI sconosciuto: '{provider}' - AI disabilitata")
                return None
        except Exception as e:
            print(f"⚠️  Errore init AI provider '{provider}': {e} - AI disabilitata")
            return None

    def _load_config(self, config_path):
        """Load config"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"📝 Config loaded: {config_path}")
            return config
        except Exception as e:
            print(f"❌ Config error: {e}")
            sys.exit(1)
    
    async def start(self):
        """Start system"""
        print("\n🚀 Starting HYBRID system...")
        
        # Initialize lights
        print("\n💡 Initializing lights...")
        lights_config = self.config.get('lights', {})
        self.wiz_controller = WizController(lights_config)
        
        success = await self.wiz_controller.initialize()
        if not success:
            print("❌ Failed to connect lights!")
            return
        
        # Initialize effect engine
        print("\n⚡ Initializing HYBRID effect engine...")
        effects_config = self.config.get('effects', {})
        self.effect_engine = EffectEngine(
            self.wiz_controller,
            self.audio_analyzer,
            effects_config
        )
        
        # Connect Shazam
        print("\n🎵 Connecting Shazam to effect engine...")
        self.effect_engine.shazam_client = self.shazam_client
        print("   ✅ Shazam connected!")

        # Connect AI provider
        if self.ai_suggester:
            self.effect_engine.ai_suggester = self.ai_suggester
            print(f"   ✅ AI provider connected!")

        # Connect Spotify analyzer
        spotify_cfg = self.config.get('spotify', {})
        if spotify_cfg.get('enabled', False):
            try:
                from recognition.spotify_analyzer import SpotifyAnalyzer
                self.effect_engine.spotify_analyzer = SpotifyAnalyzer(
                    spotify_cfg['client_id'],
                    spotify_cfg['client_secret']
                )
                print(f"   ✅ Spotify section analyzer connected!")
            except Exception as e:
                print(f"   ⚠️  Spotify non disponibile: {e}")
        
        # Start audio
        self.audio_analyzer.start()
        
        # Start effects
        await self.effect_engine.start()
        
        self.is_running = True
        
        print("\n" + "=" * 60)
        print("✅ HYBRID SYSTEM RUNNING!")
        print("=" * 60)
        print(f"\n🎵 Features:")
        print(f"   🎼 Song recognition: Every 30s")
        print(f"   🤖 AI effect suggestions: Genre-based")
        print(f"   🎚️  Audio reactive: Bass/Mid/Beat")
        print(f"   🔇 Silence detection: Auto-dim")
        print(f"   💡 Lights: {self.wiz_controller.get_light_count()}")
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.stop()
    
    async def stop(self):
        """Stop system"""
        print("\n🛑 Stopping...")
        
        self.is_running = False
        
        if self.audio_analyzer:
            self.audio_analyzer.stop()
        
        if self.effect_engine:
            await self.effect_engine.stop()
        
        if self.wiz_controller:
            await self.wiz_controller.turn_off()
        
        print("✅ Stopped")


async def main():
    """Entry point"""
    app = LightJockey()
    
    def signal_handler(sig, frame):
        print("\n⚠️  Interrupt...")
        asyncio.create_task(app.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await app.start()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        await app.stop()


if __name__ == '__main__':
    asyncio.run(main())
