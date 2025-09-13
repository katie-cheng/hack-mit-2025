import os
import time
import httpx
from typing import Dict, Any
from .models import SmartHomeAlert, HomeStatus


class AURAVoiceService:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        if not self.api_key:
            print("⚠️ VAPI API key not configured - voice calls will be simulated")
            self.simulate_mode = True
        else:
            print("✅ VAPI configured - real voice calls enabled")
            self.simulate_mode = False

    async def send_warning_call(self, alert: SmartHomeAlert, phone_number: str) -> Dict[str, Any]:
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

    async def send_resolution_call(self, phone_number: str, home_status: HomeStatus) -> Dict[str, Any]:
        """Send the final resolution call with results"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        # Create the resolution message
        resolution_message = f"This is AURA with a final report. The home is now secure and operating on battery power. The energy sale was successful, generating a profit of ${home_status.profit_generated:.2f}. The situation is managed."
        
        # Create assistant context for the resolution call
        assistant_context = f"""
You are AURA, an AI smart home management system. You are calling a homeowner with a final report after successfully managing a weather event.

FINAL REPORT: {resolution_message}

INSTRUCTIONS:
1. Clearly communicate the final report message above
2. Provide a brief summary of what was accomplished:
   - Home is now secure and operating on battery power
   - Energy sale was successful
   - Profit generated: ${home_status.profit_generated:.2f}
   - Situation is fully managed
3. Ask if they have any questions about the actions taken
4. Keep the conversation brief and professional
5. End with reassurance that their home is protected

Remember: You are providing a positive update about successful home protection. Be confident and reassuring.
"""

        if self.simulate_mode:
            # Simulate the call for demo purposes
            print(f"📞 [SIMULATED] Resolution call to {phone_number}")
            print(f"   Message: {resolution_message}")
            return {
                "success": True,
                "call_id": f"sim_{int(time.time())}",
                "message": "Resolution call simulated successfully"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                call_payload = {
                    "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"),
                    "customer": {"number": phone_number},
                    "assistant": {
                        "firstMessage": resolution_message,
                        "model": {
                            "provider": "xai",
                            "model": "grok-3",
                            "temperature": 0.1,
                            "messages": [
                                {"role": "system", "content": assistant_context},
                                {
                                    "role": "user",
                                    "content": resolution_message,
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
                        "message": "Resolution call initiated successfully"
                    }
                else:
                    print(f"Failed to initiate resolution call: {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }

            except Exception as e:
                print(f"Failed to send resolution call: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }