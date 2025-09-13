#!/usr/bin/env python3
"""
Test script for the Home State Agent (Digital Twin)
Demonstrates the core functionality of Agent 2 in the AURA system.
"""

import asyncio
import json
from datetime import datetime
from typing import List

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from home_state_agent import (
    HomeStateAgent, 
    create_thermostat_action, create_battery_action, create_energy_sale_action
)
from home_state_models import (
    HomeStateRequest, Action, DeviceType, ActionType
)


async def test_basic_operations():
    """Test basic Home State Agent operations"""
    print("🏠 Testing Home State Agent (Digital Twin)")
    print("=" * 50)
    
    # Initialize the agent
    agent = HomeStateAgent()
    
    # Test 1: Get initial state
    print("\n📊 Initial Home State:")
    initial_state = agent.get_current_state()
    print(f"Battery: {initial_state.devices['battery'].properties['soc_percent']}%")
    print(f"Thermostat: {initial_state.devices['thermostat'].properties['temperature_f']}°F")
    print(f"Solar: {initial_state.devices['solar'].properties['current_production_kw']} kW")
    print(f"Profit: ${initial_state.financials.profit_today_usd}")
    
    # Test 2: Execute single action (thermostat)
    print("\n🌡️ Test 2: Setting thermostat to 68°F")
    thermostat_action = create_thermostat_action(temperature=68.0, mode="cool")
    request = HomeStateRequest(actions=[thermostat_action])
    
    result = await agent.process_request(request)
    print(f"Success: {result.success}")
    print(f"New temperature: {result.home_state.devices['thermostat'].properties['temperature_f']}°F")
    
    # Test 3: Execute multiple actions (emergency prep sequence)
    print("\n⚡ Test 3: Emergency Preparation Sequence")
    actions = [
        create_thermostat_action(temperature=68.0, mode="cool"),
        create_battery_action(soc_percent=100.0, backup_reserve=20.0),
        Action(
            device_type=DeviceType.GRID,
            action_type=ActionType.SET,
            parameters={"connection_status": "backup_ready"}
        )
    ]
    
    emergency_request = HomeStateRequest(
        actions=actions,
        request_id="emergency_prep_test"
    )
    
    emergency_result = await agent.process_request(emergency_request)
    print(f"Emergency prep success: {emergency_result.success}")
    print(f"Actions executed: {len(emergency_result.action_results)}")
    print(f"Battery charged to: {emergency_result.home_state.devices['battery'].properties['soc_percent']}%")
    print(f"Grid status: {emergency_result.home_state.devices['grid'].properties['connection_status']}")
    
    # Test 4: Energy sale transaction
    print("\n💰 Test 4: Energy Sale Transaction")
    energy_sale = create_energy_sale_action(energy_kwh=5.0, rate_usd_per_kwh=0.83)
    sale_request = HomeStateRequest(actions=[energy_sale])
    
    sale_result = await agent.process_request(sale_request)
    print(f"Sale success: {sale_result.success}")
    print(f"Profit generated: ${sale_result.home_state.financials.profit_today_usd}")
    print(f"Total energy sold: {sale_result.home_state.financials.total_energy_sold_kwh} kWh")
    
    # Test 5: Final state summary
    print("\n📋 Final Home State Summary:")
    final_state = agent.get_current_state()
    print(f"Processing time: {emergency_result.processing_time_ms:.2f}ms")
    print(f"Battery: {final_state.devices['battery'].properties['soc_percent']}%")
    print(f"Thermostat: {final_state.devices['thermostat'].properties['temperature_f']}°F")
    print(f"Total profit: ${final_state.financials.profit_today_usd}")
    print(f"Last updated: {final_state.last_updated}")


async def test_aura_workflow_simulation():
    """Simulate the complete AURA workflow using the Home State Agent"""
    print("\n🤖 AURA Workflow Simulation")
    print("=" * 50)
    
    agent = HomeStateAgent()
    
    # Step 1: Threat detected - prepare home
    print("\n⚠️ Step 1: Threat Assessment Agent detects heatwave")
    print("   Grid Stress Alarm Agent triggers emergency preparation...")
    
    # Step 2: Home Energy Orchestrator uses Home State Agent
    print("\n🏠 Step 2: Home Energy Orchestrator Agent calls Home State Agent")
    
    # Simulate the orchestrator's commands
    orchestrator_actions = [
        # Pre-cool the home
        create_thermostat_action(temperature=68.0, mode="cool"),
        # Charge battery to full
        create_battery_action(soc_percent=100.0, backup_reserve=20.0),
        # Prepare for grid disconnect
        Action(
            device_type=DeviceType.GRID,
            action_type=ActionType.SET,
            parameters={"connection_status": "backup_ready"}
        ),
        # Execute energy sale
        create_energy_sale_action(energy_kwh=8.15, rate_usd_per_kwh=0.83)
    ]
    
    orchestrator_request = HomeStateRequest(
        actions=orchestrator_actions,
        request_id="aura_orchestrator_workflow"
    )
    
    # Execute the complete workflow
    workflow_result = await agent.process_request(orchestrator_request)
    
    print(f"✅ Workflow completed successfully: {workflow_result.success}")
    print(f"   Actions executed: {len(workflow_result.action_results)}")
    print(f"   Processing time: {workflow_result.processing_time_ms:.2f}ms")
    
    # Step 3: Generate final message for Interface Agent
    final_state = workflow_result.home_state
    profit = final_state.financials.profit_today_usd
    battery_level = final_state.devices['battery'].properties['soc_percent']
    temp = final_state.devices['thermostat'].properties['temperature_f']
    
    interface_message = {
        "message_template": "This is AURA with a final report. The home is now secure and operating on battery power. The energy sale was successful, generating a profit of ${profit:.2f}. The situation is managed.",
        "template_data": {
            "profit": profit,
            "battery_level": battery_level,
            "temperature": temp,
            "status": "secure"
        }
    }
    
    print(f"\n📞 Step 3: Message prepared for Interface Agent (Voice Call)")
    print(f"   Template: {interface_message['message_template']}")
    print(f"   Data: {interface_message['template_data']}")
    
    return workflow_result


async def main():
    """Run all tests"""
    try:
        await test_basic_operations()
        await test_aura_workflow_simulation()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
