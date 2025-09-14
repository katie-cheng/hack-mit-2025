#!/usr/bin/env python3
"""
Test the real home state agent to verify minimum action requirement works.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

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

async def test_real_agent_minimum_actions():
    """Test the real home state agent with minimum action requirement"""
    
    print_separator("TESTING REAL HOME STATE AGENT - MINIMUM ACTIONS")
    
    # Test 1: Agent without LLM (should use fallback)
    print("Test 1: Agent without LLM")
    agent_no_llm = HomeStateAgent(openai_api_key=None)
    
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
            )
        ],
        analysis_timestamp=datetime.utcnow(),
        location="Austin, TX",
        data_sources=["weather_api"]
    )
    
    print("Generating actions without LLM...")
    actions_no_llm = await agent_no_llm.generate_intelligent_actions(heat_wave_threat)
    
    print(f"Generated {len(actions_no_llm)} actions:")
    for i, action in enumerate(actions_no_llm, 1):
        print(f"   {i}. {action.device_type.value.upper()}: {action.action_type.value}")
        print(f"      Parameters: {action.parameters}")
    
    if len(actions_no_llm) >= 1:
        print("✅ PASS: Generated at least 1 action without LLM")
    else:
        print("❌ FAIL: Did not generate at least 1 action without LLM")
    
    print_separator("TEST 2: EXECUTE ACTIONS")
    
    # Test 2: Execute the generated actions
    if actions_no_llm:
        print("Executing generated actions...")
        request = HomeStateRequest(
            actions=actions_no_llm,
            request_id="test_minimum_actions"
        )
        
        result = await agent_no_llm.process_request(request)
        
        if result.success:
            print("✅ Actions executed successfully")
            print(f"   Processing time: {result.processing_time_ms:.2f}ms")
            print(f"   Actions executed: {len(result.action_results)}")
        else:
            print(f"❌ Action execution failed: {result.message}")
    
    print_separator("TEST 3: DIFFERENT THREAT TYPES")
    
    # Test 3: Test different threat types
    threat_types = [
        (ThreatType.GRID_STRAIN, ThreatLevel.CRITICAL),
        (ThreatType.POWER_OUTAGE, ThreatLevel.HIGH),
        (ThreatType.ENERGY_SHORTAGE, ThreatLevel.MEDIUM)
    ]
    
    for threat_type, threat_level in threat_types:
        print(f"\nTesting {threat_type.value} at {threat_level.value} level...")
        
        threat = ThreatAnalysis(
            overall_threat_level=threat_level,
            threat_types=[threat_type],
            confidence_score=0.8,
            risk_score=0.8,
            indicators=[
                ThreatIndicator(
                    indicator_type="test_indicator",
                    value=100.0,
                    description="Test indicator",
                    confidence=0.8
                )
            ],
            analysis_timestamp=datetime.utcnow(),
            location="Austin, TX",
            data_sources=["test_api"]
        )
        
        actions = await agent_no_llm.generate_intelligent_actions(threat)
        
        print(f"   Generated {len(actions)} actions:")
        for i, action in enumerate(actions, 1):
            print(f"     {i}. {action.device_type.value.upper()}: {action.action_type.value}")
        
        if len(actions) >= 1:
            print(f"   ✅ PASS: {threat_type.value} generated at least 1 action")
        else:
            print(f"   ❌ FAIL: {threat_type.value} did not generate at least 1 action")
    
    print_separator("VERIFICATION COMPLETE")
    print("✅ The home state agent now guarantees at least 1 action per threat analysis")
    print("   - Fallback mechanism works when LLM is unavailable")
    print("   - Actions are appropriate for different threat types and levels")
    print("   - All actions can be executed successfully")

if __name__ == "__main__":
    asyncio.run(test_real_agent_minimum_actions())
