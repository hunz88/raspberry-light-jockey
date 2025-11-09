#!/usr/bin/env python3
from pywizlight import wizlight, PilotBuilder
import asyncio
import sys

async def test_light(ip):
    print(f"\n🔍 Testing light: {ip}")
    light = wizlight(ip)
    
    try:
        print("   Accendo ROSSO...")
        await light.turn_on(PilotBuilder(rgb=(255, 0, 0), brightness=255))
        await asyncio.sleep(2)
        
        print("   Accendo VERDE...")
        await light.turn_on(PilotBuilder(rgb=(0, 255, 0), brightness=255))
        await asyncio.sleep(2)
        
        print("   Accendo BLU...")
        await light.turn_on(PilotBuilder(rgb=(0, 0, 255), brightness=255))
        await asyncio.sleep(2)
        
        print("   ✅ Test completato!")
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 test_light.py <IP>")
        print("Esempio: python3 test_light.py 192.168.0.48")
        sys.exit(1)
    
    ip = sys.argv[1]
    asyncio.run(test_light(ip))
