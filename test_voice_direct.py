#!/usr/bin/env python3
"""
Direct test of voice service without module imports
"""

import asyncio
import os
import time
import httpx
from datetime import datetime
from typing import Dict, Any


class AURAVoiceService:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        if not self.api_key:
            print("⚠️ VAPI API key not configured - voice calls will be simulated")
            self.simulate_mode = True
        else:
            print("✅ VAPI configured - real voice calls enabled")
            self.simulate_mode = False

    async def send_warning_call(self, alert, phone_number: str) -> Dict[str, Any]:
        """Send the initial warning call to homeowner"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        # Create the warning message
        warning_message = f"This is AURA. {alert.message}"
        
        # Create assistant context for the warning call
        assistant_context = f"""
You are AURA, an AI smart home management system. You are calling a homeowner about a potential weather event.

URGENT ALERT: {alert.message}

INSTRUCTIONS:
1. Clearly communicate the urgent alert message above
2. Ask if they want you to prepare their home for the event
3. If they say "yes" or agree, respond: "Great. Executing resilience now. We'll give you a ring when we've made our plan."
4. If they say "no" or decline, respond: "Understood. We'll continue monitoring the situation and will contact you if conditions change."
5. Keep the conversation brief and professional
6. Always end with a clear next step

Remember: You are a helpful AI assistant managing their smart home. Be reassuring but urgent about the situation.
"""

        if self.simulate_mode:
            # Simulate the call for demo purposes
            print(f"📞 [SIMULATED] Warning call to {phone_number}")
            print(f"   Message: {warning_message}")
            return {
                "success": True,
                "call_id": f"sim_{int(time.time())}",
                "message": "Warning call simulated successfully"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                call_payload = {
                    "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"),
                    "customer": {"number": phone_number},
                    "assistant": {
                        "firstMessage": warning_message,
                        "model": {
                            "provider": "xai",
                            "model": "grok-3",
                            "temperature": 0.1,
                            "messages": [
                                {"role": "system", "content": assistant_context},
                                {
                                    "role": "user",
                                    "content": warning_message,
                                },
                            ],
                        },
                        "voice": {"provider": "11labs", "voiceId": "burt"},
                    },
                }

                response = await client.post(
                    "https://api.vapi.ai/call",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=call_payload,
                )

                if response.status_code == 201:
                    call_data = response.json()
                    return {
                        "success": True,
                        "call_id": call_data.get("id"),
                        "message": "Warning call initiated successfully"
                    }
                else:
                    print(f"Failed to initiate warning call: {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }

            except Exception as e:
                print(f"Failed to send warning call: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }


class WeatherEvent:
    def __init__(self, event_type, probability, severity, predicted_time, description):
        self.event_type = event_type
        self.probability = probability
        self.severity = severity
        self.predicted_time = predicted_time
        self.description = description


class SmartHomeAlert:
    def __init__(self, alert_type, weather_event, message, action_required, homeowner_consent):
        self.alert_type = alert_type
        self.weather_event = weather_event
        self.message = message
        self.action_required = action_required
        self.homeowner_consent = homeowner_consent


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
