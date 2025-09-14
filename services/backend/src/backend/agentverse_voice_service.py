"""
Voice service for AURA Smart Home Management Agent
Handles VAPI integration for voice calls
"""

import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv
from .agentverse_models import VoiceCallRequest, VoiceCallResponse

# Load environment variables
load_dotenv()


class AURAVoiceService:
    """Service for handling voice calls via VAPI"""
    
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
        self.simulate_mode = not bool(self.api_key)
        
        if self.simulate_mode:
            print("⚠️ VAPI API key not configured - voice calls will be simulated")
        else:
            print("✅ VAPI configured - real voice calls enabled")
    
    def send_warning_call(self, phone_number: str, homeowner_name: str = "Homeowner") -> VoiceCallResponse:
        """Send a warning call about weather event"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        message = f"This is AURA. Our analyst agents have detected a 92% probability of a grid-straining heatwave event at 4 pm today. Would you like us to prepare your home?"
        
        if self.simulate_mode:
            print(f"📞 [SIMULATED] Warning call to {phone_number}")
            print(f"   Message: {message}")
            return VoiceCallResponse(
                success=True,
                call_id="simulated-warning-call",
                message="Warning call simulated successfully"
            )
        
        return self._make_vapi_call(phone_number, message, "warning")
    
    def send_resolution_call(self, phone_number: str, profit: float = 4.15) -> VoiceCallResponse:
        """Send a resolution call with final report"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        message = f"This is AURA with a final report. The home is now secure and operating on battery power. The energy sale was successful, generating a profit of ${profit:.2f}. The situation is managed."
        
        if self.simulate_mode:
            print(f"📞 [SIMULATED] Resolution call to {phone_number}")
            print(f"   Message: {message}")
            return VoiceCallResponse(
                success=True,
                call_id="simulated-resolution-call",
                message="Resolution call simulated successfully"
            )
        
        return self._make_vapi_call(phone_number, message, "resolution")
    
    def _make_vapi_call(self, phone_number: str, message: str, call_type: str) -> VoiceCallResponse:
        """Make actual VAPI call"""
        try:
            url = "https://api.vapi.ai/call"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "phoneNumberId": self.phone_number_id,
                "customer": {
                    "number": phone_number
                },
                "assistant": {
                    "model": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo"
                    },
                    "voice": {
                        "provider": "11labs",
                        "voiceId": "21m00Tcm4TlvDq8ikWAM"
                    },
                    "firstMessage": message,
                    "endCallMessage": "Thank you for using AURA. Goodbye.",
                    "endCallPhrases": ["goodbye", "bye", "thank you", "thanks"]
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                call_id = result.get("id", "unknown")
                call_status = result.get("status", "unknown")
                print(f"✅ {call_type.title()} call initiated successfully to {phone_number} (ID: {call_id}, Status: {call_status})")
                return VoiceCallResponse(
                    success=True,
                    call_id=call_id,
                    message=f"{call_type.title()} call initiated successfully"
                )
            else:
                error_msg = f"Failed to initiate {call_type} call: {response.text}"
                print(f"❌ {error_msg}")
                return VoiceCallResponse(
                    success=False,
                    message=error_msg
                )
                
        except Exception as e:
            error_msg = f"Error initiating {call_type} call: {str(e)}"
            print(f"❌ {error_msg}")
            return VoiceCallResponse(
                success=False,
                message=error_msg
            )
