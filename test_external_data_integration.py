#!/usr/bin/env python3
"""
Test Home State Agent with external data integration
Demonstrates how the agent dynamically generates actions based on real-world data
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add backend path for imports
sys.path.append('/Users/eyrinkim/Documents/GitHub/hack-mit-2025/services/backend/src')

try:
    from backend.home_state_agent import (
        HomeStateAgent, create_thermostat_action, create_battery_action,
        create_energy_sale_action
    )
    from backend.home_state_models import DeviceType, ActionType, Action, HomeStateRequest
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_AVAILABLE = False

class ExternalDataProcessor:
    """Processes external data and generates appropriate home actions"""
    
    def __init__(self, agent):
        self.agent = agent
        self.action_history = []
    
    def load_external_data(self, data_file):
        """Load external data from JSON file"""
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {data_file}: {e}")
            return None
    
    def analyze_weather_data(self, weather_data):
        """Analyze weather data and generate thermostat actions"""
        actions = []
        temperature = weather_data.get("temperature_f", 75)
        heat_index = weather_data.get("heat_index_f", temperature)
        condition = weather_data.get("condition", "Clear")
        nws_alert = weather_data.get("nws_alert")
        
        print(f"    🌤️  Weather Analysis:")
        print(f"       Temperature: {temperature}°F (feels like {heat_index}°F)")
        print(f"       Condition: {condition}")
        if nws_alert:
            print(f"       Alert: {nws_alert[:50]}...")
        
        # Generate thermostat actions based on weather
        if heat_index > 100:
            # Extreme heat - aggressive cooling
            actions.append(create_thermostat_action(temperature=68, mode="cool"))
            print(f"       🥵 Extreme heat detected → Setting AC to 68°F")
        elif heat_index > 90:
            # Hot weather - moderate cooling
            actions.append(create_thermostat_action(temperature=72, mode="cool"))
            print(f"       ☀️ Hot weather → Setting AC to 72°F")
        elif temperature < 60:
            # Cold weather - heating
            actions.append(create_thermostat_action(temperature=70, mode="heat"))
            print(f"       ❄️ Cold weather → Setting heat to 70°F")
        else:
            # Comfortable weather - energy saving mode
            actions.append(create_thermostat_action(temperature=75, mode="auto"))
            print(f"       😌 Comfortable weather → Energy saving mode (75°F)")
        
        return actions
    
    def analyze_grid_data(self, grid_data):
        """Analyze grid data and generate battery/energy actions"""
        actions = []
        grid_stability = grid_data.get("grid_stability", "unknown")
        energy_price = grid_data.get("energy_price_usd_per_mwh", 0)
        frequency = grid_data.get("frequency_hz", 60)
        status = grid_data.get("status", "Normal")
        
        print(f"    ⚡ Grid Analysis:")
        print(f"       Stability: {grid_stability}")
        print(f"       Energy Price: ${energy_price}/MWh")
        print(f"       Frequency: {frequency} Hz")
        print(f"       Status: {status[:50]}...")
        
        # Generate battery actions based on grid conditions
        if grid_stability == "outage":
            # Grid outage - maximize battery backup
            actions.append(create_battery_action(soc_percent=95, backup_reserve=25))
            print(f"       🔋 Grid outage → Maximizing battery backup (95% SOC, 25% reserve)")
        elif grid_stability == "stressed":
            # Grid stressed - conserve energy
            actions.append(create_battery_action(soc_percent=80, backup_reserve=30))
            print(f"       ⚡ Grid stressed → Conserving energy (80% SOC, 30% reserve)")
        elif energy_price > 60:
            # High energy prices - use battery power
            actions.append(create_battery_action(soc_percent=60, backup_reserve=15))
            print(f"       💰 High energy prices → Using battery power (60% SOC)")
        elif energy_price < 20:
            # Low energy prices - charge battery
            actions.append(create_battery_action(soc_percent=90, backup_reserve=20))
            print(f"       💵 Low energy prices → Charging battery (90% SOC)")
        else:
            # Normal conditions - standard management
            actions.append(create_battery_action(soc_percent=75, backup_reserve=20))
            print(f"       ✅ Normal conditions → Standard management (75% SOC)")
        
        # Generate energy selling actions
        if grid_stability == "stable" and energy_price > 40:
            # Good conditions for selling energy
            sell_kwh = min(10.0, energy_price / 10)  # Scale with price
            rate = energy_price / 1000  # Convert to $/kWh
            actions.append(create_energy_sale_action(sell_kwh, rate))
            print(f"       💡 Selling {sell_kwh:.1f} kWh at ${rate:.3f}/kWh")
        
        return actions
    
    async def process_external_data(self, weather_file, grid_file):
        """Process external data and execute generated actions"""
        print(f"\n{'='*60}")
        print(f"🔄 PROCESSING EXTERNAL DATA")
        print(f"{'='*60}")
        
        # Load external data
        weather_data = self.load_external_data(weather_file)
        grid_data = self.load_external_data(grid_file)
        
        if not weather_data or not grid_data:
            print("❌ Failed to load external data")
            return None
        
        # Analyze data and generate actions
        weather_actions = self.analyze_weather_data(weather_data)
        grid_actions = self.analyze_grid_data(grid_data)
        
        # Combine all actions
        all_actions = weather_actions + grid_actions
        
        if not all_actions:
            print("    ⚠️ No actions generated from external data")
            return None
        
        print(f"\n    🎯 Generated {len(all_actions)} actions from external data")
        
        # Execute actions
        try:
            request = HomeStateRequest(
                request_id=f"external_data_{datetime.now().timestamp()}",
                actions=all_actions
            )
            
            result = await self.agent.process_request(request)
            
            print(f"\n    📋 Execution Results:")
            print(f"       Success: {result.success}")
            print(f"       Message: {result.message}")
            print(f"       Processing Time: {result.processing_time_ms:.2f}ms")
            
            if result.success:
                print(f"\n    🏠 Final Home State:")
                for device_type in [DeviceType.THERMOSTAT, DeviceType.BATTERY, DeviceType.SOLAR, DeviceType.GRID]:
                    device = result.home_state.get_device(device_type)
                    if device:
                        print(f"       {device_type.value.upper()}: {device.properties}")
                
                print(f"       💰 Financials: ${result.home_state.financials.profit_today_usd:.2f} profit today")
            
            # Log the action
            self.action_history.append({
                "timestamp": datetime.now().isoformat(),
                "weather_file": weather_file,
                "grid_file": grid_file,
                "actions": [action.__dict__ for action in all_actions],
                "result": result.__dict__ if hasattr(result, '__dict__') else str(result)
            })
            
            return result
            
        except Exception as e:
            print(f"    ❌ Error executing actions: {e}")
            return None

async def test_external_data_scenarios():
    """Test various external data scenarios"""
    print("🏠 HOME STATE AGENT - EXTERNAL DATA INTEGRATION TEST")
    print("=" * 60)
    
    if not IMPORTS_AVAILABLE:
        print("❌ Cannot run test - imports not available")
        return
    
    # Initialize agent
    print("\n🤖 Initializing Home State Agent...")
    agent = HomeStateAgent()
    processor = ExternalDataProcessor(agent)
    print("✅ Agent and data processor ready")
    
    # Test scenarios
    scenarios = [
        ("Normal conditions", "data/mock_weather_mild.json", "data/mock_grid_normal.json"),
        ("Extreme heat + Stressed grid", "data/mock_weather_data.json", "data/mock_grid_data.json"),
        ("Storm + Grid outage", "data/mock_weather_storm.json", "data/mock_grid_outage.json"),
    ]
    
    results = []
    
    for scenario_name, weather_file, grid_file in scenarios:
        print(f"\n🧪 SCENARIO: {scenario_name}")
        print(f"   Weather: {weather_file}")
        print(f"   Grid: {grid_file}")
        
        result = await processor.process_external_data(weather_file, grid_file)
        results.append((scenario_name, result))
    
    # Analyze results
    print(f"\n{'='*60}")
    print(f"📊 EXTERNAL DATA INTEGRATION ANALYSIS")
    print(f"{'='*60}")
    
    successful = sum(1 for _, result in results if result and result.success)
    total = len(results)
    
    print(f"\nScenarios Processed: {total}")
    print(f"Successful: {successful}")
    print(f"Success Rate: {successful/total*100:.1f}%")
    
    if successful > 0:
        avg_time = sum(
            result.processing_time_ms for _, result in results 
            if result and result.success
        ) / successful
        print(f"Average Processing Time: {avg_time:.2f}ms")
    
    # Show action history
    print(f"\nAction History:")
    for i, action_log in enumerate(processor.action_history, 1):
        print(f"  {i}. {action_log['timestamp']}: {len(action_log['actions'])} actions from {action_log['weather_file']} + {action_log['grid_file']}")
    
    print(f"\n🎉 EXTERNAL DATA INTEGRATION TEST COMPLETE!")
    print(f"The agent successfully demonstrated dynamic action generation")
    print(f"based on external weather and grid data.")

async def main():
    """Main test function"""
    await test_external_data_scenarios()

if __name__ == "__main__":
    asyncio.run(main())
