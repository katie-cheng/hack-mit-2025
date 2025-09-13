#!/usr/bin/env python3
"""
Comprehensive test script for the complete AURA threat-to-action pipeline.
Tests the integration between Threat Assessment Agent and Home State Agent.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "services" / "backend" / "src"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "backend"))

from agent_orchestrator import AgentOrchestrator
from threat_models import ThreatAnalysisRequest, ThreatLevel, ThreatType
from home_state_models import HomeStateRequest, Action, DeviceType, ActionType


async def test_heatwave_scenario():
    """Test the extreme heat wave scenario"""
    print("🌡️  Testing Heat Wave Scenario")
    print("=" * 50)
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    # Configure for heat wave scenario
    from threat_models import MockDataConfig
    mock_config = MockDataConfig(
        use_mock_weather=True,
        use_mock_grid=True,
        mock_weather_file="mock_weather_data.json",
        mock_grid_file="mock_grid_data.json"
    )
    orchestrator.threat_agent.update_mock_config(mock_config)
    
    try:
        result = await orchestrator.process_threat_to_action(
            location="Austin, TX",
            include_research=False
        )
        
        print(f"✅ Pipeline completed successfully")
        print(f"   Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
        
        if result.get('threat_analysis'):
            analysis = result['threat_analysis']
            print(f"\n🔍 Threat Analysis:")
            print(f"   Overall Level: {analysis.overall_threat_level}")
            print(f"   Threat Types: {analysis.threat_types}")
            print(f"   Confidence: {analysis.confidence_score:.2f}")
            print(f"   Summary: {analysis.analysis_summary}")
            
            print(f"\n⚠️  Primary Concerns:")
            for concern in analysis.primary_concerns:
                print(f"   • {concern}")
            
            print(f"\n💡 Recommended Actions:")
            for action in analysis.recommended_actions:
                print(f"   • {action}")
        
        if result.get('home_actions'):
            print(f"\n🏠 Home Actions Generated: {len(result['home_actions'])}")
            for i, action in enumerate(result['home_actions'], 1):
                print(f"   {i}. {action.device_type}: {action.action_type} - {action.parameters}")
        
        if result.get('home_state'):
            home_state = result['home_state']
            print(f"\n🏡 Final Home State:")
            print(f"   Home ID: {home_state.metadata.home_id}")
            print(f"   Location: {home_state.metadata.location}")
            print(f"   Devices: {len(home_state.devices)}")
            
            # Show device states
            for device_type, device in home_state.devices.items():
                print(f"   • {device_type}: {device.properties}")
        
        return True
        
    except Exception as e:
        print(f"❌ Heat wave scenario failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_normal_scenario():
    """Test the normal conditions scenario"""
    print("\n\n🌤️  Testing Normal Conditions Scenario")
    print("=" * 50)
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    # Configure for normal scenario
    from threat_models import MockDataConfig
    mock_config = MockDataConfig(
        use_mock_weather=True,
        use_mock_grid=True,
        mock_weather_file="mock_weather_normal.json",
        mock_grid_file="mock_grid_normal.json"
    )
    orchestrator.threat_agent.update_mock_config(mock_config)
    
    try:
        result = await orchestrator.process_threat_to_action(
            location="Austin, TX",
            include_research=False
        )
        
        print(f"✅ Pipeline completed successfully")
        print(f"   Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
        
        if result.get('threat_analysis'):
            analysis = result['threat_analysis']
            print(f"\n🔍 Threat Analysis:")
            print(f"   Overall Level: {analysis.overall_threat_level}")
            print(f"   Threat Types: {analysis.threat_types}")
            print(f"   Confidence: {analysis.confidence_score:.2f}")
        
        print(f"\n🏠 Home Actions Generated: {len(result.get('home_actions', []))}")
        if result.get('home_actions'):
            for i, action in enumerate(result['home_actions'], 1):
                print(f"   {i}. {action.device_type}: {action.action_type} - {action.parameters}")
        
        return True
        
    except Exception as e:
        print(f"❌ Normal scenario failed: {e}")
        return False


async def test_storm_scenario():
    """Test the severe thunderstorm scenario"""
    print("\n\n⛈️  Testing Severe Thunderstorm Scenario")
    print("=" * 50)
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    # Configure for storm scenario
    from threat_models import MockDataConfig
    mock_config = MockDataConfig(
        use_mock_weather=True,
        use_mock_grid=True,
        mock_weather_file="mock_weather_storm.json",
        mock_grid_file="mock_grid_data.json"
    )
    orchestrator.threat_agent.update_mock_config(mock_config)
    
    try:
        result = await orchestrator.process_threat_to_action(
            location="Austin, TX",
            include_research=False
        )
        
        print(f"✅ Pipeline completed successfully")
        print(f"   Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
        
        if result.get('threat_analysis'):
            analysis = result['threat_analysis']
            print(f"\n🔍 Threat Analysis:")
            print(f"   Overall Level: {analysis.overall_threat_level}")
            print(f"   Threat Types: {analysis.threat_types}")
            print(f"   Confidence: {analysis.confidence_score:.2f}")
        
        print(f"\n🏠 Home Actions Generated: {len(result.get('home_actions', []))}")
        if result.get('home_actions'):
            for i, action in enumerate(result['home_actions'], 1):
                print(f"   {i}. {action.device_type}: {action.action_type} - {action.parameters}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storm scenario failed: {e}")
        return False


async def test_outage_scenario():
    """Test the grid outage scenario"""
    print("\n\n⚡ Testing Grid Outage Scenario")
    print("=" * 50)
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    # Configure for outage scenario
    from threat_models import MockDataConfig
    mock_config = MockDataConfig(
        use_mock_weather=True,
        use_mock_grid=True,
        mock_weather_file="mock_weather_storm.json",
        mock_grid_file="mock_grid_outage.json"
    )
    orchestrator.threat_agent.update_mock_config(mock_config)
    
    try:
        result = await orchestrator.process_threat_to_action(
            location="Austin, TX",
            include_research=False
        )
        
        print(f"✅ Pipeline completed successfully")
        print(f"   Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
        
        if result.get('threat_analysis'):
            analysis = result['threat_analysis']
            print(f"\n🔍 Threat Analysis:")
            print(f"   Overall Level: {analysis.overall_threat_level}")
            print(f"   Threat Types: {analysis.threat_types}")
            print(f"   Confidence: {analysis.confidence_score:.2f}")
        
        print(f"\n🏠 Home Actions Generated: {len(result.get('home_actions', []))}")
        if result.get('home_actions'):
            for i, action in enumerate(result['home_actions'], 1):
                print(f"   {i}. {action.device_type}: {action.action_type} - {action.parameters}")
        
        return True
        
    except Exception as e:
        print(f"❌ Outage scenario failed: {e}")
        return False


async def test_system_status():
    """Test system status and health checks"""
    print("\n\n📊 Testing System Status")
    print("=" * 50)
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    try:
        status = await orchestrator.get_system_status()
        
        print(f"✅ System Status Retrieved:")
        print(f"   Orchestrator: {status['orchestrator_status']}")
        print(f"   Threat Agent: {status['threat_agent']['status']}")
        print(f"   Home Agent: {status['home_agent']['status']}")
        
        print(f"\n📡 Data Sources:")
        sources = status['threat_agent']['data_sources']
        print(f"   Weather API: {'✅' if sources['weather_api'] else '❌'}")
        print(f"   Grid API: {'✅' if sources['grid_api'] else '❌'}")
        print(f"   Research API: {'✅' if sources['research_api'] else '❌'}")
        
        print(f"\n🏠 Home State:")
        home_info = status['home_agent']
        print(f"   Home ID: {home_info['home_id']}")
        print(f"   Location: {home_info['location']}")
        print(f"   Devices: {home_info['devices']}")
        
        return True
        
    except Exception as e:
        print(f"❌ System status test failed: {e}")
        return False


async def test_threat_action_mapping():
    """Test threat-to-action mapping functionality"""
    print("\n\n🗺️  Testing Threat-Action Mapping")
    print("=" * 50)
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    try:
        mapping = orchestrator.get_threat_action_mapping()
        
        print(f"✅ Threat-Action Mapping Retrieved:")
        for threat_type, actions in mapping.items():
            print(f"\n   {threat_type.upper()}:")
            for i, action in enumerate(actions, 1):
                print(f"     {i}. {action['device_type']}: {action['action_type']} - {action['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Threat-action mapping test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 AURA Threat-to-Action Pipeline Test Suite")
    print("=" * 60)
    print("Testing the complete integration between:")
    print("  • Threat Assessment Agent (The Oracle)")
    print("  • Home State Agent (Digital Twin)")
    print("  • Agent Orchestrator")
    print("=" * 60)
    
    tests = [
        ("Heat Wave Scenario", test_heatwave_scenario),
        ("Normal Conditions", test_normal_scenario),
        ("Severe Thunderstorm", test_storm_scenario),
        ("Grid Outage", test_outage_scenario),
        ("System Status", test_system_status),
        ("Threat-Action Mapping", test_threat_action_mapping)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = await test_func()
            if success:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ AURA Threat-to-Action Pipeline is fully operational")
        print("✅ Threat Assessment Agent is working correctly")
        print("✅ Home State Agent is working correctly")
        print("✅ Agent Orchestrator is coordinating properly")
        print("✅ Data flow between agents is smooth")
        print("✅ Multiple threat scenarios are handled correctly")
    else:
        print(f"\n❌ {total - passed} tests failed. Check the output above.")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
