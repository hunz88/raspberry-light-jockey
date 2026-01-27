#!/usr/bin/env python3
"""
Raspberry Pi Light Jockey - HYBRID System
Song Recognition + Audio Reactive
"""

import asyncio
import yaml
import sys
import signal
import os
import re
from pathlib import Path
from dotenv import load_dotenv

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
        
        self.is_running = False
        
        print("\n🎵 Initializing audio analyzer...")
        audio_config = self.config.get('audio', {})
        self.audio_analyzer = AudioAnalyzer(audio_config)
        
        print("\n🎼 Initializing Shazam...")
        recognition_config = self.config.get('recognition', {})
        self.shazam_client = ShazamClient(recognition_config)
        
        print("✅ Light Jockey initialized!")
        print("=" * 60)
    
    def _load_config(self, config_path):
        """Load config with environment variable support"""
        try:
            # Load environment variables from .env file
            load_dotenv()

            # Read config file
            with open(config_path, 'r') as f:
                config_content = f.read()

            # Replace ${VAR_NAME} with environment variables
            def replace_env_var(match):
                var_name = match.group(1)
                value = os.getenv(var_name)
                if value is None:
                    print(f"⚠️  Warning: Environment variable {var_name} not set")
                    return match.group(0)  # Keep original ${VAR_NAME}
                return value

            config_content = re.sub(r'\$\{([^}]+)\}', replace_env_var, config_content)

            # Parse YAML
            config = yaml.safe_load(config_content)
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
        
        # 🆕 CONNECT SHAZAM
        print("\n🎵 Connecting Shazam to effect engine...")
        self.effect_engine.shazam_client = self.shazam_client
        print("   ✅ Shazam connected!")
        
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

    # Use a flag for graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        print("\n⚠️  Interrupt received...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start the app in a task
        app_task = asyncio.create_task(app.start())

        # Wait for shutdown signal or app to finish
        done, pending = await asyncio.wait(
            [app_task, asyncio.create_task(shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )

        # If shutdown was triggered, stop the app
        if shutdown_event.is_set():
            await app.stop()

        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        await app.stop()


if __name__ == '__main__':
    asyncio.run(main())
