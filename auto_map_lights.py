#!/usr/bin/env python3
"""
Auto Light Mapper
Testa tutte le luci in sequenza per mappatura facile
"""
from pywizlight import wizlight, PilotBuilder
import asyncio

# Lista delle 31 luci trovate
ALL_LIGHTS = [
    '192.168.0.173', '192.168.0.190', '192.168.0.45', '192.168.0.118',
    '192.168.0.123', '192.168.0.234', '192.168.0.82', '192.168.0.22',
    '192.168.0.231', '192.168.0.251', '192.168.0.130', '192.168.0.93',
    '192.168.0.194', '192.168.0.246', '192.168.0.108', '192.168.0.171',
    '192.168.0.70', '192.168.0.100', '192.168.0.48', '192.168.0.104',
    '192.168.0.73', '192.168.0.84', '192.168.0.35', '192.168.0.211',
    '192.168.0.120', '192.168.0.107', '192.168.0.245', '192.168.0.98',
    '192.168.0.153', '192.168.0.78', '192.168.0.37'
]

async def test_light(ip, number):
    """Flash a light RED"""
    light = wizlight(ip)
    try:
        # Flash rosso 3 volte
        for _ in range(3):
            await light.turn_on(PilotBuilder(rgb=(255, 0, 0), brightness=255))
            await asyncio.sleep(0.3)
            await light.turn_on(PilotBuilder(brightness=50))
            await asyncio.sleep(0.3)
        
        # Spegni
        await light.turn_off()
        return True
    except Exception as e:
        print(f"      ❌ Errore: {e}")
        return False

async def main():
    print("=" * 60)
    print("🗺️  AUTO LIGHT MAPPER")
    print("=" * 60)
    print("\nOgni luce lampeggerà ROSSO 3 volte.")
    print("Annota la posizione fisica!\n")
    
    input("Premi ENTER per iniziare...")
    
    for i, ip in enumerate(ALL_LIGHTS, 1):
        print(f"\n[{i}/31] Testing: {ip}")
        print("      Guarda quale lampeggia...")
        
        success = await test_light(ip, i)
        
        if success:
            position = input(f"      Posizione: ")
            print(f"      ✅ Salvato: {ip} = {position}")
        
        # Pausa tra test
        if i < len(ALL_LIGHTS):
            print("\n      Prossima luce tra 2 secondi...")
            await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Mappatura completata!")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
