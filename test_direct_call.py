#!/usr/bin/env python3
"""
Direct test of phone call functionality
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

# Import only the voice service
from backend.voice_alerts import AURAVoiceService
from backend.models import SmartHomeAlert, WeatherEvent


async def test_direct_call():
    """Test direct phone call to the specified number"""
    print("📞 Testing Direct Phone Call")
    print("=" * 40)
    
    # Initialize voice service
    voice_service = AURAVoiceService()
    
    # Test number
    phone_number = "+19259892492"
    
    # Create a test alert
    weather_event = WeatherEvent(
        event_type="heatwave",
        probability=92.0,
        severity="high",
        predicted_time="4 PM today",
        description="Our analyst agents have detected a 92% probability of a grid-straining heatwave event at 4 pm today."
    )
    
    alert = SmartHomeAlert(
        alert_type="warning",
        weather_event=weather_event,
        message="Our analyst agents have detected a 92% probability of a grid-straining heatwave event at 4 pm today. Would you like us to prepare your home?",
        action_required=True,
        homeowner_consent=False
    )
    
    print(f"📞 Sending warning call to {phone_number}")
    print(f"Message: {alert.message}")
    
    # Make the call
    result = await voice_service.send_warning_call(alert, phone_number)
    
    print(f"\nCall Result:")
    print(f"Success: {result.get('success', False)}")
    print(f"Call ID: {result.get('call_id', 'N/A')}")
    print(f"Message: {result.get('message', 'N/A')}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    
    print("\n✅ Direct call test completed!")


if __name__ == "__main__":
    asyncio.run(test_direct_call())
