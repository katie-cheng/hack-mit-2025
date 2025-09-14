import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .threat_assessment_agent import ThreatAssessmentAgent
from .threat_models import ThreatAnalysisRequest, ThreatAnalysisResult, ThreatLevel, ThreatType, MockDataConfig
from .home_state_agent import HomeStateAgent
from .home_state_models import HomeStateRequest, Action, DeviceType, ActionType
from .api_clients import MockDataClient
from .voice_alerts import AURAVoiceService
from .agentverse_voice_service import AURAVoiceService as AgentverseVoiceService
from .models import HomeownerRegistration, RegisteredHomeowner, SmartHomeAlert, WeatherEvent


class AgentOrchestrator:
    """
    Orchestrates the flow between Threat Assessment Agent and Home State Agent.
    
    The pipeline works as follows:
    1. Threat Assessment Agent analyzes environmental threats
    2. Based on threat analysis, orchestrator determines appropriate home actions
    3. Home State Agent executes the recommended actions
    4. Results are returned showing the complete threat-to-action flow
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        
        # Initialize agents with mock data by default
        mock_config = MockDataConfig(
            use_mock_weather=True,
            use_mock_grid=True,
            mock_weather_file="mock_weather_data.json",
            mock_grid_file="mock_grid_data.json"
        )
        
        self.threat_agent = ThreatAssessmentAgent(
            openai_api_key=openai_api_key,
            mock_config=mock_config
        )
        self.home_agent = HomeStateAgent(openai_api_key=openai_api_key)
        
        # Initialize voice service for phone calls
        self.voice_service = AURAVoiceService()
        
        # Initialize agentverse voice service for permission/completion calls
        self.agentverse_voice_service = AgentverseVoiceService()
        
        # Initialize mock data client for enhanced scenarios
        self.mock_client = MockDataClient(data_dir="data")
        
        # Registered homeowners for phone calls
        self.registered_homeowners: Dict[str, RegisteredHomeowner] = {}
        
        # Threat-to-action mapping rules
        self.threat_action_mapping = self._initialize_threat_action_mapping()
    
    async def initialize(self):
        """Initialize both agents"""
        print("🔄 Initializing Agent Orchestrator...")
        print("   ✅ Threat Assessment Agent (The Oracle) - Ready")
        print("   ✅ Home State Agent (Digital Twin) - Ready")
        print("   ✅ Voice Service - Ready")
        print("   ✅ Agent Orchestrator - Ready")
    
    async def register_homeowner(self, registration: HomeownerRegistration) -> Dict[str, Any]:
        """Register a new homeowner for phone call alerts"""
        try:
            # Check if phone number already registered
            if registration.phone_number in self.registered_homeowners:
                return {
                    "success": False,
                    "message": f"Phone number {registration.phone_number} is already registered"
                }
            
            # Create new homeowner
            homeowner = RegisteredHomeowner(
                id=str(int(time.time())),
                name=registration.name,
                phone_number=registration.phone_number,
                registered_at=datetime.utcnow()
            )
            
            self.registered_homeowners[registration.phone_number] = homeowner
            
            print(f"✅ Registered homeowner: {homeowner.name} ({homeowner.phone_number})")
            
            return {
                "success": True,
                "message": f"Successfully registered {homeowner.name}",
                "homeowner_id": homeowner.id
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error registering homeowner: {str(e)}"
            }
    
    async def get_registered_homeowners(self) -> Dict[str, Any]:
        """Get list of registered homeowners"""
        try:
            homeowners_list = [
                {
                    "id": h.id,
                    "name": h.name,
                    "phone_number": h.phone_number,
                    "registered_at": h.registered_at.isoformat()
                }
                for h in self.registered_homeowners.values()
            ]
            
            return {
                "success": True,
                "message": "Homeowners retrieved successfully",
                "homeowners": homeowners_list
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting homeowners: {str(e)}"
            }
    
    async def get_home_status(self) -> Dict[str, Any]:
        """Get current home status"""
        try:
            # Get current home state from the home agent
            home_state = self.home_agent.get_current_state()
            
            # Convert to agentverse format
            status_data = {
                "battery_level": home_state.battery.soc_percent,
                "thermostat_temp": home_state.thermostat.temperature,
                "market_status": home_state.market.status,
                "energy_sold": home_state.market.energy_sold_kwh,
                "profit_generated": home_state.market.profit_usd,
                "solar_charging": home_state.solar.is_charging,
                "ac_running": home_state.thermostat.mode == "cool",
                "last_updated": home_state.metadata.last_updated
            }
            
            return {
                "success": True,
                "message": "Home status retrieved successfully",
                "data": {"status": status_data}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting home status: {str(e)}"
            }
    
    async def simulate_heatwave(self) -> Dict[str, Any]:
        """Simulate heatwave response for all registered homeowners"""
        try:
            if not self.registered_homeowners:
                return {
                    "success": False,
                    "message": "No homeowners registered. Please register homeowners first."
                }
            
            # Send warning calls to all homeowners
            warning_results = []
            for phone_number, homeowner in self.registered_homeowners.items():
                print(f"📞 Sending warning call to {homeowner.name} ({phone_number})")
                result = self.agentverse_voice_service.send_warning_call(phone_number, homeowner.name)
                warning_results.append({
                    "homeowner": homeowner.name,
                    "phone_number": phone_number,
                    "success": result.success,
                    "call_id": result.call_id
                })
            
            # Wait for warning calls to be answered (30 seconds)
            print("⏳ Waiting for warning calls to be answered...")
            await asyncio.sleep(30)
            
            # Run the threat-to-action pipeline
            print("🌡️ Starting heatwave simulation...")
            pipeline_result = await self.process_threat_to_action("Austin, TX", include_research=False)
            
            # Wait a bit more before sending resolution calls
            print("⏳ Waiting before sending resolution calls...")
            await asyncio.sleep(10)
            
            # Send resolution calls after simulation
            resolution_results = []
            profit = pipeline_result.get('home_state', {}).get('profit_generated', 4.15) if pipeline_result.get('home_state') else 4.15
            
            for phone_number, homeowner in self.registered_homeowners.items():
                print(f"📞 Sending resolution call to {homeowner.name} ({phone_number})")
                result = self.agentverse_voice_service.send_resolution_call(phone_number, profit)
                resolution_results.append({
                    "homeowner": homeowner.name,
                    "phone_number": phone_number,
                    "success": result.success,
                    "call_id": result.call_id
                })
            
            return {
                "success": True,
                "message": "Heatwave simulation completed successfully",
                "data": {
                    "warning_calls": warning_results,
                    "resolution_calls": resolution_results,
                    "final_status": pipeline_result.get('home_state', {})
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during heatwave simulation: {str(e)}"
            }
    
    async def reset_simulation(self) -> Dict[str, Any]:
        """Reset simulation state"""
        try:
            await self.reset_system()
            
            return {
                "success": True,
                "message": "Simulation reset successfully - all data cleared"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error resetting simulation: {str(e)}"
            }
    
    async def handle_message(self, message: dict) -> dict:
        """Handle incoming messages from AgentVerse"""
        try:
            content = message.get("content", "").lower()
            
            # Parse command
            if "register" in content and "homeowner" in content:
                # Extract name and phone number from message
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
                    registration = HomeownerRegistration(name=name, phone_number=phone)
                    result = await self.register_homeowner(registration)
                    response_content = f"Registration: {result['message']}"
                else:
                    response_content = "Please provide a valid phone number for registration"
            
            elif "status" in content or "home status" in content:
                result = await self.get_home_status()
                response_content = f"Home Status: {result['message']}\nData: {result.get('data', {})}"
            
            elif "homeowners" in content or "registered" in content:
                result = await self.get_registered_homeowners()
                response_content = f"Homeowners: {result['message']}\nData: {result.get('homeowners', [])}"
            
            elif "simulate" in content and "heatwave" in content:
                result = await self.simulate_heatwave()
                response_content = f"Simulation: {result['message']}\nData: {result.get('data', {})}"
            
            elif "reset" in content:
                result = await self.reset_simulation()
                response_content = f"Reset: {result['message']}"
            
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
            
            return {
                "success": True,
                "response": response_content,
                "source": "AURA",
                "target": message.get("source", "agentverse")
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"Error processing message: {str(e)}",
                "source": "AURA",
                "target": message.get("source", "agentverse")
            }
    
    async def send_permission_calls(self) -> Dict[str, Any]:
        """Send permission calls to all registered homeowners"""
        try:
            if not self.registered_homeowners:
                return {
                    "success": True,
                    "message": "No homeowners registered for permission calls",
                    "calls": []
                }
            
            print(f"📞 Sending permission calls to {len(self.registered_homeowners)} homeowners")
            
            call_results = []
            for phone_number, homeowner in self.registered_homeowners.items():
                print(f"📞 Sending permission call to {homeowner.name} ({phone_number})")
                result = self.agentverse_voice_service.send_warning_call(phone_number, homeowner.name)
                call_results.append({
                    "homeowner": homeowner.name,
                    "phone_number": phone_number,
                    "success": result.success,
                    "call_id": result.call_id,
                    "message": result.message
                })
            
            return {
                "success": True,
                "message": f"Permission calls sent to {len(call_results)} homeowners",
                "calls": call_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending permission calls: {str(e)}",
                "calls": []
            }
    
    async def send_completion_calls(self, profit: float = 4.15) -> Dict[str, Any]:
        """Send completion calls to all registered homeowners"""
        try:
            if not self.registered_homeowners:
                return {
                    "success": True,
                    "message": "No homeowners registered for completion calls",
                    "calls": []
                }
            
            print(f"📞 Sending completion calls to {len(self.registered_homeowners)} homeowners")
            
            call_results = []
            for phone_number, homeowner in self.registered_homeowners.items():
                print(f"📞 Sending completion call to {homeowner.name} ({phone_number})")
                result = self.agentverse_voice_service.send_resolution_call(phone_number, profit)
                call_results.append({
                    "homeowner": homeowner.name,
                    "phone_number": phone_number,
                    "success": result.success,
                    "call_id": result.call_id,
                    "message": result.message
                })
            
            return {
                "success": True,
                "message": f"Completion calls sent to {len(call_results)} homeowners",
                "calls": call_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending completion calls: {str(e)}",
                "calls": []
            }
    
    def _initialize_threat_action_mapping(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize mapping from threat types to home actions"""
        return {
            "heat_wave": [
                {
                    "device_type": DeviceType.THERMOSTAT,
                    "action_type": ActionType.SET,
                    "parameters": {"temperature": 68.0, "mode": "cool"},
                    "priority": "high",
                    "description": "Pre-cool home to 68°F for heat wave"
                },
                {
                    "device_type": DeviceType.BATTERY,
                    "action_type": ActionType.SET,
                    "parameters": {"soc_percent": 100.0, "backup_reserve": 20.0},
                    "priority": "high",
                    "description": "Charge battery to 100% for backup power"
                }
            ],
            "grid_strain": [
                {
                    "device_type": DeviceType.BATTERY,
                    "action_type": ActionType.SET,
                    "parameters": {"soc_percent": 100.0, "backup_reserve": 30.0},
                    "priority": "high",
                    "description": "Increase backup reserve for grid instability"
                },
                {
                    "device_type": DeviceType.GRID,
                    "action_type": ActionType.SET,
                    "parameters": {"connection_status": "backup_ready"},
                    "priority": "medium",
                    "description": "Prepare for potential grid disconnect"
                }
            ],
            "power_outage": [
                {
                    "device_type": DeviceType.BATTERY,
                    "action_type": ActionType.SET,
                    "parameters": {"soc_percent": 100.0, "backup_reserve": 50.0},
                    "priority": "critical",
                    "description": "Maximize battery for outage protection"
                },
                {
                    "device_type": DeviceType.THERMOSTAT,
                    "action_type": ActionType.SET,
                    "parameters": {"temperature": 70.0, "mode": "cool"},
                    "priority": "high",
                    "description": "Optimize temperature for battery efficiency"
                }
            ],
            "energy_shortage": [
                {
                    "device_type": DeviceType.GRID,
                    "action_type": ActionType.SET,
                    "parameters": {"sell_energy": 5.0, "rate_usd_per_kwh": 0.95},
                    "priority": "high",
                    "description": "Sell excess energy at premium rate"
                },
                {
                    "device_type": DeviceType.BATTERY,
                    "action_type": ActionType.SET,
                    "parameters": {"soc_percent": 80.0, "backup_reserve": 25.0},
                    "priority": "medium",
                    "description": "Maintain optimal battery level for trading"
                }
            ]
        }
    
    async def process_threat_to_action_with_calls(self, location: str, include_research: bool = False) -> Dict[str, Any]:
        """
        Complete threat-to-action pipeline with permission and completion calls:
        1. Send permission calls to all registered homeowners
        2. Wait for responses (30 seconds)
        3. Run the existing threat-to-action pipeline
        4. Send completion calls with results
        """
        start_time = time.time()
        
        try:
            # Step 1: Send permission calls
            print(f"📞 Step 1: Sending permission calls to homeowners")
            permission_result = await self.send_permission_calls()
            
            # Wait for permission calls to be answered
            print("⏳ Waiting 30 seconds for permission calls to be answered...")
            await asyncio.sleep(30)
            
            # Step 2: Run the existing threat-to-action pipeline
            print(f"🔍 Step 2: Running threat-to-action pipeline for {location}")
            pipeline_result = await self.process_threat_to_action(location, include_research)
            
            # Step 3: Send completion calls
            print(f"📞 Step 3: Sending completion calls with results")
            profit = pipeline_result.get('home_state', {}).get('profit_generated', 4.15) if pipeline_result.get('home_state') else 4.15
            completion_result = await self.send_completion_calls(profit)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "success": pipeline_result.get('success', False),
                "message": f"Complete pipeline with calls executed for {location}",
                "permission_calls": permission_result,
                "pipeline_result": pipeline_result,
                "completion_calls": completion_result,
                "processing_time_ms": processing_time,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "message": f"Pipeline with calls execution failed: {str(e)}",
                "permission_calls": {"success": False, "calls": []},
                "pipeline_result": None,
                "completion_calls": {"success": False, "calls": []},
                "processing_time_ms": processing_time,
                "timestamp": datetime.utcnow()
            }
    
    async def process_threat_to_action(self, location: str, include_research: bool = False) -> Dict[str, Any]:
        """
        Complete threat-to-action pipeline with phone call integration:
        1. Analyze threats for location
        2. Send warning calls to registered homeowners (if high threat)
        3. Generate home actions based on threats
        4. Execute actions on home state
        5. Send resolution calls with results
        6. Return complete results
        """
        start_time = time.time()
        
        try:
            # Step 1: Threat Assessment
            print(f"🔍 Step 1: Analyzing threats for {location}")
            threat_request = ThreatAnalysisRequest(
                location=location,
                include_weather=True,
                include_grid=True,
                include_research=include_research,
                request_id=f"orchestrator_{int(datetime.utcnow().timestamp())}"
            )
            
            threat_result = await self.threat_agent.analyze_threats(threat_request)
            
            if not threat_result.success:
                return {
                    "success": False,
                    "message": f"Threat analysis failed: {threat_result.message}",
                    "threat_analysis": None,
                    "home_actions": None,
                    "home_state": None,
                    "warning_calls": [],
                    "resolution_calls": []
                }
            
            # Step 2: Send Warning Calls (if high threat level and homeowners registered)
            warning_calls = []
            if (threat_result.analysis.overall_threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] 
                and self.registered_homeowners):
                
                print(f"📞 Step 2: Sending warning calls to {len(self.registered_homeowners)} homeowners")
                
                # Create weather event for alert
                weather_event = WeatherEvent(
                    event_type="heatwave" if ThreatType.HEAT_WAVE in threat_result.analysis.threat_types else "storm",
                    probability=threat_result.analysis.confidence_score * 100,
                    severity=threat_result.analysis.overall_threat_level.value,
                    predicted_time="4 PM today",
                    description=f"Our analyst agents have detected a {threat_result.analysis.confidence_score*100:.0f}% probability of a grid-straining heatwave event at 4 pm today."
                )
                
                # Send warning calls to all registered homeowners
                for phone_number, homeowner in self.registered_homeowners.items():
                    alert = SmartHomeAlert(
                        alert_type="warning",
                        weather_event=weather_event,
                        message=f"Our analyst agents have detected a {threat_result.analysis.confidence_score*100:.0f}% probability of a grid-straining heatwave event at 4 pm today. Would you like us to prepare your home?",
                        action_required=True,
                        homeowner_consent=False
                    )
                    
                    print(f"📞 Sending warning call to {homeowner.name} ({phone_number})")
                    call_result = await self.voice_service.send_warning_call(alert, phone_number)
                    warning_calls.append({
                        "homeowner": homeowner.name,
                        "phone_number": phone_number,
                        "success": call_result.get("success", False),
                        "call_id": call_result.get("call_id"),
                        "message": call_result.get("message")
                    })
                
                # Wait for warning calls to be answered (30 seconds)
                print("⏳ Waiting for warning calls to be answered...")
                await asyncio.sleep(30)
            
            # Step 3: Generate Home Actions
            print(f"🏠 Step 3: Generating home actions based on threats")
            home_actions = self._generate_home_actions(threat_result.analysis)
            
            if not home_actions:
                return {
                    "success": True,
                    "message": "No actions required based on threat analysis",
                    "threat_analysis": threat_result.analysis,
                    "home_actions": [],
                    "home_state": self.home_agent.get_current_state(),
                    "warning_calls": warning_calls,
                    "resolution_calls": []
                }
            
            # Step 4: Execute Home Actions
            print(f"⚡ Step 4: Executing {len(home_actions)} home actions")
            home_request = HomeStateRequest(
                actions=home_actions,
                request_id=f"orchestrator_home_{int(datetime.utcnow().timestamp())}"
            )
            
            home_result = await self.home_agent.process_request(home_request)
            
            # Step 5: Send Resolution Calls (if homeowners registered and actions were taken)
            resolution_calls = []
            if self.registered_homeowners and home_result.success:
                print(f"📞 Step 5: Sending resolution calls to {len(self.registered_homeowners)} homeowners")
                
                # Wait a bit before sending resolution calls
                print("⏳ Waiting before sending resolution calls...")
                await asyncio.sleep(10)
                
                # Send resolution calls to all registered homeowners
                for phone_number, homeowner in self.registered_homeowners.items():
                    print(f"📞 Sending resolution call to {homeowner.name} ({phone_number})")
                    call_result = await self.voice_service.send_resolution_call(phone_number, home_result.home_state)
                    resolution_calls.append({
                        "homeowner": homeowner.name,
                        "phone_number": phone_number,
                        "success": call_result.get("success", False),
                        "call_id": call_result.get("call_id"),
                        "message": call_result.get("message")
                    })
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "message": f"Complete threat-to-action pipeline executed for {location}",
                "threat_analysis": threat_result.analysis,
                "home_actions": home_actions,
                "home_result": home_result,
                "home_state": home_result.home_state,
                "warning_calls": warning_calls,
                "resolution_calls": resolution_calls,
                "processing_time_ms": processing_time,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "message": f"Pipeline execution failed: {str(e)}",
                "threat_analysis": None,
                "home_actions": None,
                "home_state": None,
                "warning_calls": [],
                "resolution_calls": [],
                "processing_time_ms": processing_time,
                "timestamp": datetime.utcnow()
            }
    
    def _generate_home_actions(self, threat_analysis) -> List[Action]:
        """Dynamically generate home actions based on specific threat parameters"""
        if not threat_analysis:
            return []
        
        actions = []
        
        # Extract threat parameters from indicators
        threat_params = self._extract_threat_parameters(threat_analysis)
        
        # Generate actions based on specific threat types and parameters
        for threat_type in threat_analysis.threat_types:
            if threat_type == ThreatType.HEAT_WAVE:
                actions.extend(self._generate_heat_wave_actions(threat_params, threat_analysis.overall_threat_level))
            elif threat_type == ThreatType.GRID_STRAIN:
                actions.extend(self._generate_grid_strain_actions(threat_params, threat_analysis.overall_threat_level))
            elif threat_type == ThreatType.POWER_OUTAGE:
                actions.extend(self._generate_power_outage_actions(threat_params, threat_analysis.overall_threat_level))
            elif threat_type == ThreatType.ENERGY_SHORTAGE:
                actions.extend(self._generate_energy_shortage_actions(threat_params, threat_analysis.overall_threat_level))
        
        # Add emergency actions based on overall threat level
        if threat_analysis.overall_threat_level == ThreatLevel.CRITICAL:
            actions.extend(self._generate_critical_emergency_actions(threat_params))
        elif threat_analysis.overall_threat_level == ThreatLevel.HIGH:
            actions.extend(self._generate_high_priority_actions(threat_params))
        
        # Remove duplicate actions (same device + action type)
        actions = self._deduplicate_actions(actions)
        
        return actions
    
    def _extract_threat_parameters(self, threat_analysis) -> Dict[str, Any]:
        """Extract specific threat parameters from analysis indicators"""
        params = {
            "temperature": None,
            "grid_demand": None,
            "humidity": None,
            "wind_speed": None,
            "heat_index": None,
            "grid_frequency": None,
            "reserve_margin": None
        }
        
        for indicator in threat_analysis.indicators:
            if indicator.indicator_type == "temperature":
                params["temperature"] = indicator.value
            elif indicator.indicator_type == "grid_demand":
                params["grid_demand"] = indicator.value
            elif indicator.indicator_type == "humidity":
                params["humidity"] = indicator.value
            elif indicator.indicator_type == "wind_speed":
                params["wind_speed"] = indicator.value
            elif indicator.indicator_type == "heat_index":
                params["heat_index"] = indicator.value
            elif indicator.indicator_type == "grid_frequency":
                params["grid_frequency"] = indicator.value
            elif indicator.indicator_type == "reserve_margin":
                params["reserve_margin"] = indicator.value
        
        return params
    
    def _generate_heat_wave_actions(self, params: Dict[str, Any], threat_level: ThreatLevel) -> List[Action]:
        """Generate actions specific to heat wave threats"""
        actions = []
        temp = params.get("temperature")
        
        if temp is None:
            return actions
        
        # Dynamic temperature-based cooling strategy
        if temp > 105:
            # Extreme heat - aggressive cooling
            target_temp = 65
            backup_reserve = 40
            fan_mode = "high"
        elif temp > 100:
            # Very hot - strong cooling
            target_temp = 68
            backup_reserve = 30
            fan_mode = "high"
        elif temp > 95:
            # Hot - moderate cooling
            target_temp = 70
            backup_reserve = 25
            fan_mode = "auto"
        elif temp > 90:
            # Warm - light cooling
            target_temp = 72
            backup_reserve = 20
            fan_mode = "auto"
        else:
            # Mild - minimal action
            target_temp = 74
            backup_reserve = 15
            fan_mode = "auto"
        
        # Thermostat actions
        actions.append(Action(
            device_type=DeviceType.THERMOSTAT,
            action_type=ActionType.SET,
            parameters={
                "temperature": target_temp,
                "mode": "cool",
                "fan_mode": fan_mode
            }
        ))
        
        # Battery actions based on heat severity
        if temp > 95:
            actions.append(Action(
                device_type=DeviceType.BATTERY,
                action_type=ActionType.SET,
                parameters={
                    "soc_percent": 100.0,
                    "backup_reserve": backup_reserve
                }
            ))
        
        return actions
    
    def _generate_grid_strain_actions(self, params: Dict[str, Any], threat_level: ThreatLevel) -> List[Action]:
        """Generate actions specific to grid strain threats"""
        actions = []
        demand = params.get("grid_demand")
        frequency = params.get("grid_frequency")
        
        if demand is None:
            return actions
        
        # Dynamic grid demand response
        if demand > 80000:
            # Critical demand - maximize backup
            soc_target = 100
            backup_reserve = 50
            grid_mode = "backup_ready"
            energy_sale = False
        elif demand > 75000:
            # High demand - increase backup
            soc_target = 95
            backup_reserve = 40
            grid_mode = "conservation"
            energy_sale = False
        elif demand > 70000:
            # Elevated demand - prepare for strain
            soc_target = 90
            backup_reserve = 30
            grid_mode = "monitoring"
            energy_sale = True
        else:
            # Normal demand - standard operation
            soc_target = 80
            backup_reserve = 20
            grid_mode = "normal"
            energy_sale = True
        
        # Battery actions
        actions.append(Action(
            device_type=DeviceType.BATTERY,
            action_type=ActionType.SET,
            parameters={
                "soc_percent": soc_target,
                "backup_reserve": backup_reserve
            }
        ))
        
        # Grid actions
        actions.append(Action(
            device_type=DeviceType.GRID,
            action_type=ActionType.SET,
            parameters={
                "connection_status": grid_mode
            }
        ))
        
        # Energy trading based on grid conditions
        if energy_sale and demand > 70000:
            # Sell energy when demand is high
            actions.append(Action(
                device_type=DeviceType.GRID,
                action_type=ActionType.SET,
                parameters={
                    "sell_energy": 3.0,
                    "rate_usd_per_kwh": 0.95
                }
            ))
        
        return actions
    
    def _generate_power_outage_actions(self, params: Dict[str, Any], threat_level: ThreatLevel) -> List[Action]:
        """Generate actions specific to power outage threats"""
        actions = []
        
        # Maximize battery for outage protection
        actions.append(Action(
            device_type=DeviceType.BATTERY,
            action_type=ActionType.SET,
            parameters={
                "soc_percent": 100.0,
                "backup_reserve": 60.0
            }
        ))
        
        # Optimize temperature for battery efficiency
        actions.append(Action(
            device_type=DeviceType.THERMOSTAT,
            action_type=ActionType.SET,
            parameters={
                "temperature": 70.0,
                "mode": "cool"
            }
        ))
        
        # Prepare grid for disconnection
        actions.append(Action(
            device_type=DeviceType.GRID,
            action_type=ActionType.SET,
            parameters={
                "connection_status": "outage_prep"
            }
        ))
        
        return actions
    
    def _generate_energy_shortage_actions(self, params: Dict[str, Any], threat_level: ThreatLevel) -> List[Action]:
        """Generate actions specific to energy shortage threats"""
        actions = []
        
        # Sell excess energy at premium rate
        actions.append(Action(
            device_type=DeviceType.GRID,
            action_type=ActionType.SET,
            parameters={
                "sell_energy": 5.0,
                "rate_usd_per_kwh": 1.20
            }
        ))
        
        # Maintain optimal battery level for trading
        actions.append(Action(
            device_type=DeviceType.BATTERY,
            action_type=ActionType.SET,
            parameters={
                "soc_percent": 85.0,
                "backup_reserve": 25.0
            }
        ))
        
        return actions
    
    def _generate_critical_emergency_actions(self, params: Dict[str, Any]) -> List[Action]:
        """Generate critical emergency actions"""
        actions = []
        
        # Maximum battery backup
        actions.append(Action(
            device_type=DeviceType.BATTERY,
            action_type=ActionType.SET,
            parameters={
                "soc_percent": 100.0,
                "backup_reserve": 50.0
            }
        ))
        
        # Emergency cooling
        actions.append(Action(
            device_type=DeviceType.THERMOSTAT,
            action_type=ActionType.SET,
            parameters={
                "temperature": 65.0,
                "mode": "cool",
                "fan_mode": "high"
            }
        ))
        
        # Grid emergency mode
        actions.append(Action(
            device_type=DeviceType.GRID,
            action_type=ActionType.SET,
            parameters={
                "connection_status": "emergency"
            }
        ))
        
        return actions
    
    def _generate_high_priority_actions(self, params: Dict[str, Any]) -> List[Action]:
        """Generate high priority actions"""
        actions = []
        
        # Increased battery backup
        actions.append(Action(
            device_type=DeviceType.BATTERY,
            action_type=ActionType.SET,
            parameters={
                "soc_percent": 95.0,
                "backup_reserve": 35.0
            }
        ))
        
        # Prepared cooling
        actions.append(Action(
            device_type=DeviceType.THERMOSTAT,
            action_type=ActionType.SET,
            parameters={
                "temperature": 68.0,
                "mode": "cool"
            }
        ))
        
        return actions
    
    def _deduplicate_actions(self, actions: List[Action]) -> List[Action]:
        """Remove duplicate actions (same device + action type)"""
        seen = set()
        unique_actions = []
        
        for action in actions:
            key = (action.device_type, action.action_type)
            if key not in seen:
                seen.add(key)
                unique_actions.append(action)
            else:
                # Replace with the latest action for the same device+type
                for i, existing_action in enumerate(unique_actions):
                    if (existing_action.device_type == action.device_type and 
                        existing_action.action_type == action.action_type):
                        unique_actions[i] = action
                        break
        
        return unique_actions
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get status of both agents and orchestrator"""
        threat_status = self.threat_agent.get_data_source_status()
        home_state = self.home_agent.get_current_state()
        
        return {
            "orchestrator_status": "active",
            "threat_agent": {
                "status": "active",
                "data_sources": {
                    "weather_api": threat_status.weather_api,
                    "grid_api": threat_status.grid_api,
                    "research_api": threat_status.research_api
                }
            },
            "home_agent": {
                "status": "active",
                "home_id": home_state.metadata.home_id,
                "location": home_state.metadata.location,
                "devices": len(home_state.devices)
            },
            "timestamp": datetime.utcnow()
        }
    
    async def reset_system(self):
        """Reset both agents to initial state and clear registered homeowners"""
        self.home_agent.reset_to_initial_state()
        self.registered_homeowners.clear()
        print("🔄 System reset completed - both agents restored to initial state and homeowners cleared")
    
    def get_threat_action_mapping(self) -> Dict[str, Any]:
        """Get the current threat-to-action mapping rules"""
        return self.threat_action_mapping
    
    def update_threat_action_mapping(self, threat_type: str, actions: List[Dict[str, Any]]):
        """Update threat-to-action mapping rules"""
        self.threat_action_mapping[threat_type] = actions
        print(f"🔄 Updated threat-action mapping for {threat_type}")


# Global orchestrator instance
orchestrator = AgentOrchestrator()
