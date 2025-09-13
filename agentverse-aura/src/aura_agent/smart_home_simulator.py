"""
Smart home simulator for AURA Smart Home Management Agent
Simulates smart home device responses to weather events
"""

import asyncio
import time
from datetime import datetime
from typing import Callable, Optional
from .models import HomeStatus


class SmartHomeSimulator:
    """Simulates smart home device responses"""
    
    def __init__(self, home_status: HomeStatus, status_callback: Optional[Callable] = None):
        self.home_status = home_status
        self.status_callback = status_callback
        self.simulating = False
    
    async def simulate_heatwave_response(self) -> None:
        """Simulate smart home response to heatwave event"""
        if self.simulating:
            print("⚠️ Simulation already in progress")
            return
        
        self.simulating = True
        print("🌡️ Starting heatwave response simulation...")
        
        try:
            # Step 1: Pre-cooling home to 68°F
            await self._pre_cool_home()
            
            # Step 2: Charging battery to 100%
            await self._charge_battery()
            
            # Step 3: Executing energy sale
            await self._execute_energy_sale()
            
            print("✅ Heatwave response simulation completed!")
            
        except Exception as e:
            print(f"❌ Simulation error: {str(e)}")
        finally:
            self.simulating = False
    
    async def _pre_cool_home(self) -> None:
        """Pre-cool the home to 68°F"""
        print("❄️ Step 1: Pre-cooling home to 68°F...")
        
        current_temp = self.home_status.thermostat_temp
        target_temp = 68.0
        
        while current_temp > target_temp:
            current_temp -= 0.5
            self.home_status.thermostat_temp = current_temp
            self.home_status.ac_running = True
            self.home_status.last_updated = datetime.utcnow()
            
            print(f"   🌡️ Temperature: {current_temp}°F")
            
            if self.status_callback:
                self.status_callback(self.home_status)
            
            await asyncio.sleep(0.5)
    
    async def _charge_battery(self) -> None:
        """Charge battery to 100%"""
        print("🔋 Step 2: Charging battery to 100%...")
        
        current_battery = self.home_status.battery_level
        target_battery = 100.0
        
        while current_battery < target_battery:
            current_battery += 5.0
            self.home_status.battery_level = min(current_battery, target_battery)
            self.home_status.solar_charging = True
            self.home_status.last_updated = datetime.utcnow()
            
            print(f"   🔋 Battery: {int(self.home_status.battery_level)}%")
            
            if self.status_callback:
                self.status_callback(self.home_status)
            
            await asyncio.sleep(0.5)
    
    async def _execute_energy_sale(self) -> None:
        """Execute energy sale on the market"""
        print("💰 Step 3: Executing energy sale...")
        
        # Update market status to executing
        self.home_status.market_status = "executing_sale"
        self.home_status.last_updated = datetime.utcnow()
        
        print("   📊 Market: Executing Sale...")
        
        if self.status_callback:
            self.status_callback(self.home_status)
        
        await asyncio.sleep(1.0)
        
        # Complete the sale
        self.home_status.market_status = "success"
        self.home_status.energy_sold = 5.0
        self.home_status.profit_generated = 4.15
        self.home_status.last_updated = datetime.utcnow()
        
        print(f"   ✅ SUCCESS: Sold {self.home_status.energy_sold} kWh for ${self.home_status.profit_generated}")
        
        if self.status_callback:
            self.status_callback(self.home_status)
    
    def reset_simulation(self) -> None:
        """Reset home status to initial state"""
        self.home_status.battery_level = 45.0
        self.home_status.thermostat_temp = 72.0
        self.home_status.market_status = "monitoring"
        self.home_status.energy_sold = 0.0
        self.home_status.profit_generated = 0.0
        self.home_status.solar_charging = False
        self.home_status.ac_running = False
        self.home_status.last_updated = datetime.utcnow()
        
        print("🔄 Home status reset to initial state")
        
        if self.status_callback:
            self.status_callback(self.home_status)
