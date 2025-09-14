#!/usr/bin/env python3
"""
Test the full integration with permission and completion calls
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

# Set environment variables from agentverse-aura
os.environ["VAPI_API_KEY"] = "12d842aa-4073-4298-bada-d22aaecd3cec"
os.environ["VAPI_PHONE_NUMBER_ID"] = "7fad3e7f-a086-4e6d-b516-35a4c5523036"

from agent_orchestrator import AgentOrchestrator
from models import HomeownerRegistration


async def test_full_integration():
    """Test the full integration with permission and completion calls"""
    print("🧪 Testing Full Integration with Permission and Completion Calls")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    # Test 1: Register homeowners
    print("\n📝 Step 1: Registering homeowners")
    print("-" * 40)
    
    # Register test homeowners
    homeowners = [
        HomeownerRegistration(name="John Smith", phone_number="+19259892492"),
        HomeownerRegistration(name="Jane Doe", phone_number="+14155797749")
    ]
    
    for homeowner in homeowners:
        result = await orchestrator.register_homeowner(homeowner)
        print(f"Registration result: {result}")
    
    # Test 2: Get registered homeowners
    print("\n👥 Step 2: Getting registered homeowners")
    print("-" * 40)
    
    homeowners_result = await orchestrator.get_registered_homeowners()
    print(f"Registered homeowners: {len(homeowners_result.get('homeowners', []))}")
    
    # Test 3: Run the full pipeline with calls
    print("\n🚀 Step 3: Running full pipeline with permission and completion calls")
    print("-" * 40)
    
    # This will trigger permission calls, then run the pipeline, then completion calls
    result = await orchestrator.process_threat_to_action_with_calls("Austin, TX", include_research=False)
    
    print(f"\nPipeline Result:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Processing time: {result.get('processing_time_ms', 0):.2f}ms")
    
    # Permission calls results
    permission_calls = result.get('permission_calls', {})
    print(f"\n📞 Permission Calls:")
    print(f"  Success: {permission_calls.get('success', False)}")
    print(f"  Message: {permission_calls.get('message', 'N/A')}")
    print(f"  Calls made: {len(permission_calls.get('calls', []))}")
    
    for call in permission_calls.get('calls', []):
        print(f"    - {call['homeowner']} ({call['phone_number']}): {call['success']}")
    
    # Pipeline results
    pipeline_result = result.get('pipeline_result', {})
    print(f"\n🔍 Pipeline Results:")
    print(f"  Success: {pipeline_result.get('success', False)}")
    print(f"  Message: {pipeline_result.get('message', 'N/A')}")
    print(f"  Warning calls: {len(pipeline_result.get('warning_calls', []))}")
    print(f"  Resolution calls: {len(pipeline_result.get('resolution_calls', []))}")
    
    # Completion calls results
    completion_calls = result.get('completion_calls', {})
    print(f"\n📞 Completion Calls:")
    print(f"  Success: {completion_calls.get('success', False)}")
    print(f"  Message: {completion_calls.get('message', 'N/A')}")
    print(f"  Calls made: {len(completion_calls.get('calls', []))}")
    
    for call in completion_calls.get('calls', []):
        print(f"    - {call['homeowner']} ({call['phone_number']}): {call['success']}")
    
    # Test 4: Reset system
    print("\n🔄 Step 4: Resetting system")
    print("-" * 40)
    
    await orchestrator.reset_system()
    homeowners_after_reset = await orchestrator.get_registered_homeowners()
    print(f"Homeowners after reset: {len(homeowners_after_reset.get('homeowners', []))}")
    
    print("\n✅ Full integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_full_integration())
