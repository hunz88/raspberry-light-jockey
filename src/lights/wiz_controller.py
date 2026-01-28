"""
Wiz Lights Controller
Manages communication with Wiz RGB lights via UDP protocol
"""

import asyncio
from pywizlight import wizlight, discovery, PilotBuilder
import time


class WizController:
    """Controller for Wiz RGB lights"""

    def __init__(self, config):
        self.config = config
        self.lights = []
        self.light_ips = []
        self.light_macs = []  # 🆕 Store MAC addresses
        self.light_info = []  # 🆕 Store full info (IP, MAC, name)

        # Settings
        self.timeout = config.get('timeout', 2)
        self.max_retries = config.get('max_retries', 3)
        self.auto_discover = config.get('auto_discover', True)
        self.manual_ips = config.get('manual_ips', [])
        self.use_mac_addresses = config.get('use_mac_addresses', False)  # 🆕
        self.light_mapping = config.get('light_mapping', [])  # 🆕 MAC->Zone mapping

        # State
        self.is_connected = False
        self.last_color = None
        self.last_brightness = None

        print("💡 Wiz controller initialized")
        if self.use_mac_addresses:
            print(f"   🔐 Using MAC address mapping ({len(self.light_mapping)} configured)")
    
    async def discover_lights(self, return_info=False):
        """Discover Wiz lights on the network

        Args:
            return_info: If True, return list of light info dicts instead of bool
        """
        print("🔍 Discovering Wiz lights...")

        try:
            # Discover lights
            bulbs = await discovery.discover_lights(
                broadcast_space=self.config.get('broadcast_address', '255.255.255.255')
            )

            if bulbs:
                self.lights = []
                self.light_ips = []
                self.light_macs = []
                self.light_info = []

                for bulb in bulbs:
                    # Get MAC address
                    try:
                        state = await bulb.updateState()
                        mac = state.get_mac() if hasattr(state, 'get_mac') else bulb.mac
                    except:
                        mac = getattr(bulb, 'mac', 'unknown')

                    # Store info
                    info = {
                        'ip': bulb.ip,
                        'mac': mac,
                        'name': f"Light {bulb.ip.split('.')[-1]}",
                        'bulb': bulb
                    }

                    self.lights.append(bulb)
                    self.light_ips.append(bulb.ip)
                    self.light_macs.append(mac)
                    self.light_info.append(info)

                print(f"✅ Found {len(bulbs)} Wiz light(s):")
                for info in self.light_info:
                    print(f"   - {info['ip']} (MAC: {info['mac']})")

                self.is_connected = True

                if return_info:
                    return self.light_info.copy()
                return True
            else:
                print("⚠️ No Wiz lights found via discovery")
                if return_info:
                    return []
                return False

        except Exception as e:
            print(f"❌ Error during discovery: {e}")
            import traceback
            traceback.print_exc()
            if return_info:
                return []
            return False
    
    def add_manual_lights(self):
        """Add lights manually by IP address"""
        if not self.manual_ips:
            return False
        
        print(f"📝 Adding {len(self.manual_ips)} manual light(s)...")
        
        for ip in self.manual_ips:
            try:
                light = wizlight(ip)
                self.lights.append(light)
                self.light_ips.append(ip)
                print(f"   + {ip}")
            except Exception as e:
                print(f"   ❌ Failed to add {ip}: {e}")
        
        if self.lights:
            self.is_connected = True
            return True
        return False
    
    async def initialize(self):
        """Initialize connection to lights"""
        success = False

        # If using MAC address mapping, discover and then reorder
        if self.use_mac_addresses and self.light_mapping:
            print("🔐 Initializing with MAC address mapping...")
            success = await self.discover_lights()

            if success:
                success = await self._apply_mac_mapping()

        # Try auto-discovery first
        elif self.auto_discover:
            success = await self.discover_lights()

        # Fall back to manual IPs
        if not success and self.manual_ips:
            success = self.add_manual_lights()

        if success:
            print(f"✅ Successfully connected to {len(self.lights)} light(s)")
        else:
            print("❌ No lights found or connected")

        return success

    async def _apply_mac_mapping(self):
        """Apply MAC address mapping to reorder lights"""
        print("🔄 Applying MAC address mapping...")

        # Create MAC -> bulb dict
        mac_to_bulb = {}
        for info in self.light_info:
            mac_to_bulb[info['mac']] = info['bulb']

        # Reorder lights based on mapping
        ordered_lights = []
        ordered_ips = []
        ordered_macs = []
        ordered_info = []

        for mapping in self.light_mapping:
            mac = mapping.get('mac')
            if mac in mac_to_bulb:
                bulb = mac_to_bulb[mac]
                ordered_lights.append(bulb)
                ordered_ips.append(bulb.ip)
                ordered_macs.append(mac)
                ordered_info.append({
                    'ip': bulb.ip,
                    'mac': mac,
                    'name': mapping.get('name', f"Light {mac[-5:]}"),
                    'zone': mapping.get('zone', 'unknown'),
                    'position': mapping.get('position', 0),
                    'bulb': bulb
                })
                print(f"   ✅ {mac} → {mapping.get('name')} (Position {mapping.get('position')})")
            else:
                print(f"   ⚠️  MAC {mac} not found - skipping")

        if ordered_lights:
            self.lights = ordered_lights
            self.light_ips = ordered_ips
            self.light_macs = ordered_macs
            self.light_info = ordered_info
            print(f"✅ Mapped {len(ordered_lights)} lights by MAC address")
            return True
        else:
            print("❌ No lights matched MAC mapping")
            return False
    
    async def set_color(self, r, g, b, brightness=None):
        """
        Set color for all lights
        
        Args:
            r, g, b: RGB values (0-255)
            brightness: optional brightness (0-255)
        """
        if not self.lights:
            return False
        
        # Clamp values
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        
        if brightness is not None:
            brightness = max(0, min(255, int(brightness)))
        
        # Send to all lights
        tasks = []
        for light in self.lights:
            task = self._set_light_color(light, r, g, b, brightness)
            tasks.append(task)
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        success_count = sum(1 for result in results if result is True)
        
        # Cache last color
        self.last_color = (r, g, b)
        if brightness is not None:
            self.last_brightness = brightness
        
        return success_count > 0
    
    async def _set_light_color(self, light, r, g, b, brightness=None):
        """Set color for a single light with retry logic"""
        for attempt in range(self.max_retries):
            try:
                if brightness is not None:
                    pilot = PilotBuilder(rgb=(r, g, b), brightness=brightness)
                else:
                    pilot = PilotBuilder(rgb=(r, g, b))
                
                await light.turn_on(pilot)
                return True
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.1)
                else:
                    print(f"❌ Failed to set color on {light.ip}: {e}")
                    return False
        
        return False
    
    async def set_brightness(self, brightness):
        """
        Set brightness for all lights
        
        Args:
            brightness: brightness value (0-255)
        """
        if not self.lights:
            return False
        
        brightness = max(0, min(255, int(brightness)))
        
        tasks = []
        for light in self.lights:
            tasks.append(self._set_light_brightness(light, brightness))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if r is True)
        
        self.last_brightness = brightness
        
        return success_count > 0
    
    async def _set_light_brightness(self, light, brightness):
        """Set brightness for a single light with retry"""
        for attempt in range(self.max_retries):
            try:
                pilot = PilotBuilder(brightness=brightness)
                await light.turn_on(pilot)
                return True
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.1)
                else:
                    print(f"❌ Failed to set brightness on {light.ip}: {e}")
                    return False
        return False
    
    async def turn_off(self):
        """Turn off all lights"""
        if not self.lights:
            return False
        
        tasks = []
        for light in self.lights:
            tasks.append(self._turn_off_light(light))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if r is True)
        
        return success_count > 0
    
    async def _turn_off_light(self, light):
        """Turn off a single light"""
        try:
            await light.turn_off()
            return True
        except Exception as e:
            print(f"❌ Failed to turn off {light.ip}: {e}")
            return False
    
    async def get_state(self):
        """Get current state of first light (for monitoring)"""
        if not self.lights:
            return None
        
        try:
            light = self.lights[0]
            state = await light.updateState()
            
            return {
                'on': state.get_state(),
                'brightness': state.get_brightness(),
                'rgb': state.get_rgb(),
                'available': True
            }
        except Exception as e:
            print(f"❌ Failed to get state: {e}")
            return {
                'on': False,
                'brightness': 0,
                'rgb': (0, 0, 0),
                'available': False
            }
    
    def get_light_count(self):
        """Get number of connected lights"""
        return len(self.lights)
    
    def get_light_ips(self):
        """Get list of light IP addresses"""
        return self.light_ips.copy()

    def get_light_info_list(self):
        """Get list of light info (IP, MAC, name, zone, position)"""
        return [
            {
                'ip': info['ip'],
                'mac': info['mac'],
                'name': info.get('name', f"Light {info['ip'].split('.')[-1]}"),
                'zone': info.get('zone', 'unassigned'),
                'position': info.get('position', -1)
            }
            for info in self.light_info
        ]

    async def identify_light(self, ip_or_mac, duration=5):
        """
        Identify a light by making it flash RED for specified duration

        Args:
            ip_or_mac: IP address or MAC address of light
            duration: How long to flash in seconds (default 5)

        Returns:
            bool: Success or failure
        """
        print(f"🔍 Identifying light: {ip_or_mac}")

        # Find the light
        light = None
        for info in self.light_info:
            if info['ip'] == ip_or_mac or info['mac'] == ip_or_mac:
                light = info['bulb']
                break

        if not light:
            print(f"❌ Light not found: {ip_or_mac}")
            return False

        try:
            # Flash RED for duration
            flash_count = int(duration * 2)  # 0.5s on, 0.5s off
            pilot_red = PilotBuilder(rgb=(255, 0, 0), brightness=255)
            pilot_off = PilotBuilder(rgb=(0, 0, 0), brightness=0)

            for i in range(flash_count):
                await light.turn_on(pilot_red)
                await asyncio.sleep(0.5)
                await light.turn_on(pilot_off)
                await asyncio.sleep(0.5)

            print(f"✅ Identified light: {ip_or_mac}")
            return True

        except Exception as e:
            print(f"❌ Failed to identify light {ip_or_mac}: {e}")
            return False

    def find_light_by_mac(self, mac):
        """Find light info by MAC address"""
        for info in self.light_info:
            if info['mac'] == mac:
                return info
        return None


# Synchronous wrapper functions for easier use
def init_lights_sync(config):
    """Synchronous wrapper for light initialization"""
    controller = WizController(config)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        success = loop.run_until_complete(controller.initialize())
        return controller if success else None
    finally:
        loop.close()


def set_color_sync(controller, r, g, b, brightness=None):
    """Synchronous wrapper for setting color"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(controller.set_color(r, g, b, brightness))
    finally:
        loop.close()
