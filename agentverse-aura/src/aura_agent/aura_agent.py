"""
AURA Smart Home Management Agent for FetchAI AgentVerse
Main agent class that handles smart home management and voice calls
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

# Try to import AgentVerse, fallback to base class if not available
try:
    from agentverse.agent import Agent
    from agentverse.message import Message
    AGENTVERSE_AVAILABLE = True
except ImportError:
    # Fallback base class for testing without AgentVerse
    class Agent:
        def __init__(self, name: str = "BaseAgent", **kwargs):
            self.name = name
    
    class Message:
        def __init__(self, content: str, source: str, target: str):
            self.content = content
            self.source = source
            self.target = target
    
    AGENTVERSE_AVAILABLE = False

from .models import (
    HomeStatus, Homeowner, WeatherEvent, VoiceCallRequest, VoiceCallResponse,
    SimulationRequest, SimulationResponse, AgentResponse
)
from .voice_service import AURAVoiceService
from .smart_home_simulator import SmartHomeSimulator


class AURAAgent(Agent):
    """AURA Smart Home Management Agent"""
    
    def __init__(self, name: str = "AURA", **kwargs):
        super().__init__(name=name, **kwargs)
        
        # Initialize services
        self.voice_service = AURAVoiceService()
        self.home_status = HomeStatus()
        self.simulator = SmartHomeSimulator(self.home_status, self._update_status)
        self.registered_homeowners: Dict[str, Homeowner] = {}
        
        agentverse_status = "✅ AgentVerse enabled" if AGENTVERSE_AVAILABLE else "⚠️ AgentVerse not available (using fallback)"
        print(f"✅ AURA Agent '{name}' initialized successfully - {agentverse_status}")
    
    def _update_status(self, status: HomeStatus) -> None:
        """Callback for status updates"""
        self.home_status = status
    
    async def register_homeowner(self, name: str, phone_number: str) -> AgentResponse:
        """Register a new homeowner"""
        try:
            # Check if phone number already registered
            if phone_number in self.registered_homeowners:
                return AgentResponse(
                    success=False,
                    message=f"Phone number {phone_number} is already registered"
                )
            
            # Create new homeowner
            homeowner = Homeowner(name=name, phone_number=phone_number)
            self.registered_homeowners[phone_number] = homeowner
            
            print(f"✅ Registered homeowner: {name} ({phone_number})")
            
            return AgentResponse(
                success=True,
                message=f"Successfully registered {name}",
                data={"homeowner": homeowner.dict()}
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error registering homeowner: {str(e)}"
            )
    
    async def get_home_status(self) -> AgentResponse:
        """Get current home status"""
        try:
            return AgentResponse(
                success=True,
                message="Home status retrieved successfully",
                data={"status": self.home_status.dict()}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error getting home status: {str(e)}"
            )
    
    async def get_registered_homeowners(self) -> AgentResponse:
        """Get list of registered homeowners"""
        try:
            homeowners_list = [
                {"name": h.name, "phone_number": h.phone_number, "registered_at": h.registered_at.isoformat()}
                for h in self.registered_homeowners.values()
            ]
            
            return AgentResponse(
                success=True,
                message="Homeowners retrieved successfully",
                data={"homeowners": homeowners_list}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error getting homeowners: {str(e)}"
            )
    
    async def simulate_heatwave(self) -> AgentResponse:
        """Simulate heatwave response for all registered homeowners"""
        try:
            if not self.registered_homeowners:
                return AgentResponse(
                    success=False,
                    message="No homeowners registered. Please register homeowners first."
                )
            
            # Send warning calls to all homeowners
            warning_results = []
            for phone_number, homeowner in self.registered_homeowners.items():
                print(f"📞 Sending warning call to {homeowner.name} ({phone_number})")
                result = self.voice_service.send_warning_call(phone_number, homeowner.name)
                warning_results.append({
                    "homeowner": homeowner.name,
                    "phone_number": phone_number,
                    "success": result.success,
                    "call_id": result.call_id
                })
            
            # Wait for warning calls to be answered (30 seconds)
            print("⏳ Waiting for warning calls to be answered...")
            await asyncio.sleep(30)
            
            # Start simulation
            print("🌡️ Starting heatwave simulation...")
            await self.simulator.simulate_heatwave_response()
            
            # Wait a bit more before sending resolution calls
            print("⏳ Waiting before sending resolution calls...")
            await asyncio.sleep(10)
            
            # Send resolution calls after simulation
            resolution_results = []
            for phone_number, homeowner in self.registered_homeowners.items():
                print(f"📞 Sending resolution call to {homeowner.name} ({phone_number})")
                result = self.voice_service.send_resolution_call(phone_number, self.home_status.profit_generated)
                resolution_results.append({
                    "homeowner": homeowner.name,
                    "phone_number": phone_number,
                    "success": result.success,
                    "call_id": result.call_id
                })
            
            return AgentResponse(
                success=True,
                message="Heatwave simulation completed successfully",
                data={
                    "warning_calls": warning_results,
                    "resolution_calls": resolution_results,
                    "final_status": self.home_status.dict()
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error during heatwave simulation: {str(e)}"
            )
    
    async def reset_simulation(self) -> AgentResponse:
        """Reset simulation state"""
        try:
            self.simulator.reset_simulation()
            self.registered_homeowners.clear()
            
            return AgentResponse(
                success=True,
                message="Simulation reset successfully - all data cleared"
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error resetting simulation: {str(e)}"
            )
    
    async def handle_message(self, message: Message) -> Message:
        """Handle incoming messages from AgentVerse"""
        try:
            content = message.content.lower()
            
            # Parse command
            if "register" in content and "homeowner" in content:
                # Extract name and phone number from message
                # This is a simplified parser - in production you'd want more robust parsing
                parts = content.split()
                name = "Unknown"
                phone = None
                
                for i, part in enumerate(parts):
                    if part.isdigit() and len(part) >= 10:
                        phone = part
                        if i > 0:
                            name = parts[i-1]
                        break
                
                if phone:
                    result = await self.register_homeowner(name, phone)
                    response_content = f"Registration: {result.message}"
                else:
                    response_content = "Please provide a valid phone number for registration"
            
            elif "status" in content or "home status" in content:
                result = await self.get_home_status()
                response_content = f"Home Status: {result.message}\nData: {result.data}"
            
            elif "homeowners" in content or "registered" in content:
                result = await self.get_registered_homeowners()
                response_content = f"Homeowners: {result.message}\nData: {result.data}"
            
            elif "simulate" in content and "heatwave" in content:
                result = await self.simulate_heatwave()
                response_content = f"Simulation: {result.message}\nData: {result.data}"
            
            elif "reset" in content:
                result = await self.reset_simulation()
                response_content = f"Reset: {result.message}"
            
            else:
                response_content = """
AURA Smart Home Management Agent Commands:
- Register homeowner: "register homeowner [name] [phone]"
- Get home status: "status" or "home status"
- Get homeowners: "homeowners" or "registered"
- Simulate heatwave: "simulate heatwave"
- Reset simulation: "reset"

Example: "register homeowner John +1234567890"
                """
            
            return Message(
                content=response_content,
                source=self.name,
                target=message.source
            )
            
        except Exception as e:
            return Message(
                content=f"Error processing message: {str(e)}",
                source=self.name,
                target=message.source
            )
