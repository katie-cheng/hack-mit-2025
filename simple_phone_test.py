#!/usr/bin/env python3
"""
Simple test script for phone call integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend src directory to the path
backend_src = Path(__file__).parent / "services" / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Change to the backend directory for proper imports
os.chdir(backend_src)

# Import only what we need
from backend.agent_orchestrator import AgentOrchestrator
from backend.models import HomeownerRegistration


async def test_phone_integration():
    """Test the phone call integration"""
    print("🧪 Testing Phone Call Integration in Agent Orchestrator")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    # Test 1: Register homeowners
    print("\n📝 Test 1: Registering homeowners")
    print("-" * 40)
    
    # Register test homeowners
    homeowners = [
        HomeownerRegistration(name="John Smith", phone_number="+1234567890"),
        HomeownerRegistration(name="Jane Doe", phone_number="+1987654321")
    ]
    
    for homeowner in homeowners:
        result = await orchestrator.register_homeowner(homeowner)
        print(f"Registration result: {result}")
    
    # Test 2: Get registered homeowners
    print("\n👥 Test 2: Getting registered homeowners")
    print("-" * 40)
    
    homeowners_result = await orchestrator.get_registered_homeowners()
    print(f"Registered homeowners: {homeowners_result}")
    
    # Test 3: Run threat-to-action pipeline with phone calls
    print("\n🌡️ Test 3: Running threat-to-action pipeline with phone calls")
    print("-" * 40)
    
    # This will trigger warning calls if high threat is detected
    result = await orchestrator.process_threat_to_action("Austin, TX", include_research=False)
    
    print(f"\nPipeline Result:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Warning calls: {len(result.get('warning_calls', []))}")
    print(f"Resolution calls: {len(result.get('resolution_calls', []))}")
    
    if result.get('warning_calls'):
        print("\n📞 Warning Call Details:")
        for call in result['warning_calls']:
            print(f"  - {call['homeowner']} ({call['phone_number']}): {call['success']}")
    
    if result.get('resolution_calls'):
        print("\n📞 Resolution Call Details:")
        for call in result['resolution_calls']:
            print(f"  - {call['homeowner']} ({call['phone_number']}): {call['success']}")
    
    # Test 4: Reset system
    print("\n🔄 Test 4: Resetting system")
    print("-" * 40)
    
    await orchestrator.reset_system()
    homeowners_after_reset = await orchestrator.get_registered_homeowners()
    print(f"Homeowners after reset: {len(homeowners_after_reset.get('homeowners', []))}")
    
    print("\n✅ Phone call integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_phone_integration())
