#!/usr/bin/env python3
"""
Simple test for the LLM-based intelligent action generation in HomeStateAgent.
Tests the generate_intelligent_actions method with various threat scenarios.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent / "services" / "backend" / "src"))

# Direct imports to avoid module loading issues
from backend.home_state_models import HomeStateRequest, Action, DeviceType, ActionType, HomeState, HomeMetadata, FinancialData, DeviceState
from backend.threat_models import ThreatAnalysis, ThreatLevel, ThreatType, ThreatIndicator

# Import the HomeStateAgent class directly
import importlib.util
spec = importlib.util.spec_from_file_location("home_state_agent", "/Users/eyrinkim/Documents/GitHub/hack-mit-2025/services/backend/src/backend/home_state_agent.py")
home_state_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(home_state_agent_module)
HomeStateAgent = home_state_agent_module.HomeStateAgent

def print_separator(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

def print_json(data, title="JSON Output"):
    print(f"\n{title}:")
    print(json.dumps(data, indent=2, default=str))

async def test_llm_intelligent_actions():
    """Test the LLM-based intelligent action generation"""
    
    print_separator("INITIALIZING HOME STATE AGENT WITH LLM")
    
    # Initialize the home state agent with a mock OpenAI API key
    # In a real test, you would use a valid API key
    agent = HomeStateAgent(openai_api_key="test-key")
    
    # Check if LLM is available
    if not agent.llm:
        print("❌ LLM not available - cannot test intelligent action generation")
        print("   This test requires a valid OpenAI API key")
        return
    
    print("✅ LLM initialized successfully")
    
    # Print initial state
    print("\nInitial Home State:")
    initial_state = agent.get_current_state()
    print_json(initial_state.dict(), "Initial State")
    
    print_separator("TEST 1: HEAT WAVE THREAT")
    
    # Test 1: Heat wave threat
    heat_wave_threat = ThreatAnalysis(
        overall_threat_level=ThreatLevel.HIGH,
        threat_types=[ThreatType.HEAT_WAVE],
        confidence_score=0.85,
        risk_score=0.85,
        indicators=[
            ThreatIndicator(
                indicator_type="temperature",
                value=105.0,
                description="Temperature reaching 105°F",
                confidence=0.9
            ),
            ThreatIndicator(
                indicator_type="heat_index",
                value=115.0,
                description="Heat index at 115°F",
                confidence=0.85
            ),
            ThreatIndicator(
                indicator_type="humidity",
                value=75.0,
                description="High humidity at 75%",
                confidence=0.8
            )
        ],
        analysis_timestamp=datetime.utcnow(),
        location="Austin, TX",
        data_sources=["weather_api"]
    )
    
    print("Input Threat Analysis:")
    print_json(heat_wave_threat.dict(), "Heat Wave Threat")
    
    # Generate intelligent actions
    print("\n🤖 Generating intelligent actions for heat wave...")
    heat_wave_actions = await agent.generate_intelligent_actions(heat_wave_threat)
    
    print(f"\nGenerated {len(heat_wave_actions)} intelligent actions:")
    for i, action in enumerate(heat_wave_actions, 1):
        print(f"   {i}. {action.device_type.value.upper()}: {action.action_type.value}")
        print(f"      Parameters: {action.parameters}")
    
    print_separator("TEST 2: GRID STRAIN THREAT")
    
    # Test 2: Grid strain threat
    grid_strain_threat = ThreatAnalysis(
        overall_threat_level=ThreatLevel.CRITICAL,
        threat_types=[ThreatType.GRID_STRAIN],
        confidence_score=0.92,
        risk_score=0.92,
        indicators=[
            ThreatIndicator(
                indicator_type="grid_demand",
                value=80000,
                description="Grid demand at 80,000 MW",
                confidence=0.9
            ),
            ThreatIndicator(
                indicator_type="grid_frequency",
                value=59.5,
                description="Grid frequency dropping to 59.5 Hz",
                confidence=0.85
            ),
            ThreatIndicator(
                indicator_type="reserve_margin",
                value=3.2,
                description="Critical reserve margin at 3.2%",
                confidence=0.95
            )
        ],
        analysis_timestamp=datetime.utcnow(),
        location="Austin, TX",
        data_sources=["grid_api"]
    )
    
    print("Input Threat Analysis:")
    print_json(grid_strain_threat.dict(), "Grid Strain Threat")
    
    # Generate intelligent actions
    print("\n🤖 Generating intelligent actions for grid strain...")
    grid_strain_actions = await agent.generate_intelligent_actions(grid_strain_threat)
    
    print(f"\nGenerated {len(grid_strain_actions)} intelligent actions:")
    for i, action in enumerate(grid_strain_actions, 1):
        print(f"   {i}. {action.device_type.value.upper()}: {action.action_type.value}")
        print(f"      Parameters: {action.parameters}")
    
    print_separator("TEST 3: POWER OUTAGE THREAT")
    
    # Test 3: Power outage threat
    power_outage_threat = ThreatAnalysis(
        overall_threat_level=ThreatLevel.CRITICAL,
        threat_types=[ThreatType.POWER_OUTAGE],
        confidence_score=0.95,
        risk_score=0.95,
        indicators=[
            ThreatIndicator(
                indicator_type="grid_frequency",
                value=58.5,
                description="Grid frequency critically low at 58.5 Hz",
                confidence=0.95
            ),
            ThreatIndicator(
                indicator_type="wind_speed",
                value=45.0,
                description="High winds at 45 mph",
                confidence=0.8
            ),
            ThreatIndicator(
                indicator_type="grid_demand",
                value=82000,
                description="Extreme grid demand at 82,000 MW",
                confidence=0.9
            )
        ],
        analysis_timestamp=datetime.utcnow(),
        location="Austin, TX",
        data_sources=["grid_api", "weather_api"]
    )
    
    print("Input Threat Analysis:")
    print_json(power_outage_threat.dict(), "Power Outage Threat")
    
    # Generate intelligent actions
    print("\n🤖 Generating intelligent actions for power outage...")
    power_outage_actions = await agent.generate_intelligent_actions(power_outage_threat)
    
    print(f"\nGenerated {len(power_outage_actions)} intelligent actions:")
    for i, action in enumerate(power_outage_actions, 1):
        print(f"   {i}. {action.device_type.value.upper()}: {action.action_type.value}")
        print(f"      Parameters: {action.parameters}")
    
    print_separator("TEST 4: ENERGY SHORTAGE THREAT")
    
    # Test 4: Energy shortage threat
    energy_shortage_threat = ThreatAnalysis(
        overall_threat_level=ThreatLevel.HIGH,
        threat_types=[ThreatType.ENERGY_SHORTAGE],
        confidence_score=0.88,
        risk_score=0.88,
        indicators=[
            ThreatIndicator(
                indicator_type="reserve_margin",
                value=2.1,
                description="Critical reserve margin at 2.1%",
                confidence=0.95
            ),
            ThreatIndicator(
                indicator_type="grid_demand",
                value=85000,
                description="Peak demand at 85,000 MW",
                confidence=0.9
            )
        ],
        analysis_timestamp=datetime.utcnow(),
        location="Austin, TX",
        data_sources=["grid_api"]
    )
    
    print("Input Threat Analysis:")
    print_json(energy_shortage_threat.dict(), "Energy Shortage Threat")
    
    # Generate intelligent actions
    print("\n🤖 Generating intelligent actions for energy shortage...")
    energy_shortage_actions = await agent.generate_intelligent_actions(energy_shortage_threat)
    
    print(f"\nGenerated {len(energy_shortage_actions)} intelligent actions:")
    for i, action in enumerate(energy_shortage_actions, 1):
        print(f"   {i}. {action.device_type.value.upper()}: {action.action_type.value}")
        print(f"      Parameters: {action.parameters}")
    
    print_separator("TEST 5: EXECUTE INTELLIGENT ACTIONS")
    
    # Test 5: Execute some of the generated actions
    if heat_wave_actions:
        print("Executing heat wave actions...")
        request = HomeStateRequest(
            actions=heat_wave_actions,
            request_id="test_heat_wave_execution"
        )
        
        result = await agent.process_request(request)
        print_json(result.dict(), "Heat Wave Action Execution Result")
    
    print_separator("TEST 6: LLM ERROR HANDLING")
    
    # Test 6: Test with invalid threat data to see error handling
    invalid_threat = ThreatAnalysis(
        overall_threat_level=ThreatLevel.LOW,
        threat_types=[],  # Empty threat types
        confidence_score=0.0,
        risk_score=0.0,
        indicators=[],  # Empty indicators
        analysis_timestamp=datetime.utcnow(),
        location="",
        data_sources=[]
    )
    
    print("Input Invalid Threat Analysis:")
    print_json(invalid_threat.dict(), "Invalid Threat")
    
    print("\n🤖 Generating intelligent actions for invalid threat...")
    invalid_actions = await agent.generate_intelligent_actions(invalid_threat)
    
    print(f"\nGenerated {len(invalid_actions)} intelligent actions:")
    for i, action in enumerate(invalid_actions, 1):
        print(f"   {i}. {action.device_type.value.upper()}: {action.action_type.value}")
        print(f"      Parameters: {action.parameters}")
    
    print_separator("TEST SUMMARY")
    
    # Summary of all tests
    all_actions = {
        "Heat Wave": heat_wave_actions,
        "Grid Strain": grid_strain_actions,
        "Power Outage": power_outage_actions,
        "Energy Shortage": energy_shortage_actions,
        "Invalid Threat": invalid_actions
    }
    
    print("Summary of Generated Actions:")
    for threat_type, actions in all_actions.items():
        print(f"   {threat_type}: {len(actions)} actions")
        if actions:
            device_types = [action.device_type.value for action in actions]
            print(f"      Device types: {', '.join(set(device_types))}")
    
    print("\n✅ LLM intelligent action generation test completed!")
    print("   Check the outputs above to verify:")
    print("   1. Actions are generated for different threat types")
    print("   2. Actions are appropriate for the threat level")
    print("   3. Actions use valid device types and parameters")
    print("   4. Error handling works for invalid inputs")

if __name__ == "__main__":
    asyncio.run(test_llm_intelligent_actions())
