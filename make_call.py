#!/usr/bin/env python3
"""
Make a real phone call to +19259892492
Usage: VAPI_API_KEY=your_key VAPI_PHONE_NUMBER_ID=your_id python make_call.py
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
        self.phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
        
        if not self.api_key or not self.phone_number_id:
            print("❌ VAPI credentials not configured!")
            print("   Set VAPI_API_KEY and VAPI_PHONE_NUMBER_ID environment variables")
            print("   Example: VAPI_API_KEY=your_key VAPI_PHONE_NUMBER_ID=your_id python make_call.py")
            exit(1)
        else:
            print("✅ VAPI configured - making REAL call")

    async def send_warning_call(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send the warning call to homeowner"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        # Create assistant context for the warning call
        assistant_context = f"""
You are AURA, an AI smart home management system. You are calling a homeowner about a potential weather event.

URGENT ALERT: {message}

INSTRUCTIONS:
1. Clearly communicate the urgent alert message above
2. Ask if they want you to prepare their home for the event
3. If they say "yes" or agree, respond: "Great. Executing resilience now. We'll give you a ring when we've made our plan."
4. If they say "no" or decline, respond: "Understood. We'll continue monitoring the situation and will contact you if conditions change."
5. Keep the conversation brief and professional
6. Always end with a clear next step

Remember: You are a helpful AI assistant managing their smart home. Be reassuring but urgent about the situation.
"""
        
        async with httpx.AsyncClient() as client:
            try:
                call_payload = {
                    "phoneNumberId": self.phone_number_id,
                    "customer": {"number": phone_number},
                    "assistant": {
                        "firstMessage": f"This is AURA. {message}",
                        "model": {
                            "provider": "xai",
                            "model": "grok-3",
                            "temperature": 0.1,
                            "messages": [
                                {"role": "system", "content": assistant_context},
                                {
                                    "role": "user",
                                    "content": message,
                                },
                            ],
                        },
                        "voice": {"provider": "11labs", "voiceId": "burt"},
                    },
                }

                print(f"📞 Making REAL call to {phone_number}")
                print(f"   Using phone number ID: {self.phone_number_id}")
                print(f"   Message: {message}")
                
                response = await client.post(
                    "https://api.vapi.ai/call",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=call_payload,
                )

                print(f"   Response status: {response.status_code}")
                print(f"   Response body: {response.text}")

                if response.status_code == 201:
                    call_data = response.json()
                    return {
                        "success": True,
                        "call_id": call_data.get("id"),
                        "message": "Warning call initiated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code} - {response.text}"
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }


async def make_call():
    """Make a real phone call to +19259892492"""
    print("📞 Making Phone Call to +19259892492")
    print("=" * 50)
    
    # Initialize voice service
    voice_service = AURAVoiceService()
    
    # Test number
    phone_number = "+19259892492"
    
    # Message
    message = "Our analyst agents have detected a 92% probability of a grid-straining heatwave event at 4 pm today. Would you like us to prepare your home?"
    
    # Make the call
    result = await voice_service.send_warning_call(phone_number, message)
    
    print(f"\nCall Result:")
    print(f"Success: {result.get('success', False)}")
    print(f"Call ID: {result.get('call_id', 'N/A')}")
    print(f"Message: {result.get('message', 'N/A')}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    
    if result.get('success'):
        print("\n✅ Call initiated successfully! Check your phone.")
    else:
        print("\n❌ Call failed. Check the error message above.")


if __name__ == "__main__":
    asyncio.run(make_call())
