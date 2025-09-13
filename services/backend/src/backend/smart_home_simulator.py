import asyncio
import httpx
from datetime import datetime
from typing import Optional
from .models import HomeStatus


class SmartHomeSimulator:
    def __init__(self, home_status_ref=None):
        self.base_url = "http://localhost:8000"  # Backend URL for status updates
        self.home_status_ref = home_status_ref  # Reference to global home_status
        
    async def simulate_heatwave_response(self):
        """
        Simulate the complete heatwave response sequence:
        1. Increase AC (pre-cool to 68°F)
        2. Charge solar panels (battery to 100%)
        3. Execute energy sale (market transaction)
        """
        print("🌡️ Starting heatwave response simulation...")
        
        # Step 1: Pre-cool the home (AC to 68°F)
        await self._simulate_ac_precooling()
        
        # Step 2: Charge battery to 100%
        await self._simulate_battery_charging()
        
        # Step 3: Execute energy sale
        await self._simulate_energy_sale()
        
        # Step 4: Notify completion
        await self._notify_simulation_complete()
        
        print("✅ Heatwave response simulation completed!")

    async def _simulate_ac_precooling(self):
        """Simulate AC pre-cooling to 68°F"""
        print("❄️ Step 1: Pre-cooling home to 68°F...")
        
        # Simulate gradual temperature decrease
        current_temp = 72.0
        target_temp = 68.0
        steps = 8  # 8 steps to reach target
        
        for i in range(steps + 1):
            temp = current_temp - (current_temp - target_temp) * (i / steps)
            
            # Update home status
            await self._update_home_status({
                "thermostat_temp": temp,
                "ac_running": True,
                "last_updated": datetime.utcnow()
            })
            
            print(f"   🌡️ Temperature: {temp:.1f}°F")
            await asyncio.sleep(0.5)  # 0.5 second delay between updates

    async def _simulate_battery_charging(self):
        """Simulate battery charging to 100%"""
        print("🔋 Step 2: Charging battery to 100%...")
        
        # Simulate rapid battery charging
        current_level = 45.0
        target_level = 100.0
        steps = 11  # 11 steps to reach 100%
        
        for i in range(steps + 1):
            level = current_level + (target_level - current_level) * (i / steps)
            
            # Update home status
            await self._update_home_status({
                "battery_level": level,
                "solar_charging": True,
                "last_updated": datetime.utcnow()
            })
            
            print(f"   🔋 Battery: {level:.0f}%")
            await asyncio.sleep(0.3)  # 0.3 second delay between updates

    async def _simulate_energy_sale(self):
        """Simulate energy market sale"""
        print("💰 Step 3: Executing energy sale...")
        
        # Step 3a: Change market status to "executing_sale"
        await self._update_home_status({
            "market_status": "executing_sale",
            "last_updated": datetime.utcnow()
        })
        print("   📊 Market: Executing Sale...")
        await asyncio.sleep(1.0)
        
        # Step 3b: Complete the sale
        energy_sold = 5.0  # kWh
        profit = 4.15  # USD
        
        await self._update_home_status({
            "market_status": "success",
            "energy_sold": energy_sold,
            "profit_generated": profit,
            "last_updated": datetime.utcnow()
        })
        print(f"   ✅ SUCCESS: Sold {energy_sold} kWh for ${profit:.2f}")

    async def _update_home_status(self, updates: dict):
        """Update the home status with new values"""
        try:
            if self.home_status_ref:
                # Update the global home_status object
                for key, value in updates.items():
                    if hasattr(self.home_status_ref, key):
                        setattr(self.home_status_ref, key, value)
                print(f"   📊 Status update: {updates}")
            else:
                print(f"   📊 Status update: {updates}")
        except Exception as e:
            print(f"   ❌ Error updating status: {e}")

    async def _notify_simulation_complete(self):
        """Notify that the simulation is complete"""
        print("📞 Notifying simulation completion...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/simulation/complete")
                if response.status_code == 200:
                    print("   ✅ Simulation completion notification sent")
                else:
                    print(f"   ❌ Failed to notify completion: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error notifying completion: {e}")

    async def reset_simulation(self):
        """Reset the simulation to initial state"""
        print("🔄 Resetting simulation...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/simulation/reset")
                if response.status_code == 200:
                    print("   ✅ Simulation reset successfully")
                else:
                    print(f"   ❌ Failed to reset simulation: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error resetting simulation: {e}")
