import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .home_state_models import (
    HomeStateRequest, HomeStateResult, HomeState, Action, ActionResult,
    DeviceType, ActionType, DeviceState, HomeMetadata, FinancialData
)

class HomeStateValidationError(Exception):
    """Custom exception for home state validation errors"""
    pass

class DeviceOperationError(Exception):
    """Custom exception for device operation errors"""
    pass

class StateValidator:
    """Centralized state validation with bounds checking and business logic"""
    
    # Validation constants
    MIN_TEMPERATURE_F = 60.0
    MAX_TEMPERATURE_F = 90.0
    MIN_BATTERY_SOC = 0.0
    MAX_BATTERY_SOC = 100.0
    MIN_BACKUP_RESERVE = 0.0
    MAX_BACKUP_RESERVE = 100.0
    MIN_SOLAR_PRODUCTION = 0.0
    MAX_SOLAR_PRODUCTION = 50.0  # kW
    
    @staticmethod
    def validate_thermostat_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize thermostat properties"""
        validated = {}
        
        if "temperature_f" in properties:
            temp = float(properties["temperature_f"])
            if temp < StateValidator.MIN_TEMPERATURE_F:
                raise HomeStateValidationError(
                    f"Temperature {temp}°F below minimum {StateValidator.MIN_TEMPERATURE_F}°F"
                )
            if temp > StateValidator.MAX_TEMPERATURE_F:
                raise HomeStateValidationError(
                    f"Temperature {temp}°F above maximum {StateValidator.MAX_TEMPERATURE_F}°F"
                )
            validated["temperature_f"] = temp
            validated["target_temperature_f"] = temp
        
        if "mode" in properties:
            mode = properties["mode"]
            if mode not in ["heat", "cool", "auto", "off"]:
                raise HomeStateValidationError(f"Invalid thermostat mode: {mode}")
            validated["mode"] = mode
            
        if "fan_mode" in properties:
            fan_mode = properties["fan_mode"]
            if fan_mode not in ["auto", "on", "circulate"]:
                raise HomeStateValidationError(f"Invalid fan mode: {fan_mode}")
            validated["fan_mode"] = fan_mode
            
        return validated
    
    @staticmethod
    def validate_battery_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize battery properties"""
        validated = {}
        
        if "soc_percent" in properties:
            soc = float(properties["soc_percent"])
            if soc < StateValidator.MIN_BATTERY_SOC or soc > StateValidator.MAX_BATTERY_SOC:
                raise HomeStateValidationError(
                    f"Battery SOC {soc}% must be between {StateValidator.MIN_BATTERY_SOC}% and {StateValidator.MAX_BATTERY_SOC}%"
                )
            validated["soc_percent"] = soc
        
        if "backup_reserve_percent" in properties:
            reserve = float(properties["backup_reserve_percent"])
            if reserve < StateValidator.MIN_BACKUP_RESERVE or reserve > StateValidator.MAX_BACKUP_RESERVE:
                raise HomeStateValidationError(
                    f"Backup reserve {reserve}% must be between {StateValidator.MIN_BACKUP_RESERVE}% and {StateValidator.MAX_BACKUP_RESERVE}%"
                )
            validated["backup_reserve_percent"] = reserve
            
        if "grid_charging" in properties:
            validated["grid_charging"] = bool(properties["grid_charging"])
            
        return validated
    
    @staticmethod
    def validate_solar_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize solar properties"""
        validated = {}
        
        if "current_production_kw" in properties:
            production = float(properties["current_production_kw"])
            if production < StateValidator.MIN_SOLAR_PRODUCTION:
                raise HomeStateValidationError(
                    f"Solar production {production}kW cannot be negative"
                )
            if production > StateValidator.MAX_SOLAR_PRODUCTION:
                raise HomeStateValidationError(
                    f"Solar production {production}kW exceeds maximum {StateValidator.MAX_SOLAR_PRODUCTION}kW"
                )
            validated["current_production_kw"] = production
            
        if "efficiency_percent" in properties:
            efficiency = float(properties["efficiency_percent"])
            if efficiency < 0 or efficiency > 100:
                raise HomeStateValidationError(
                    f"Solar efficiency {efficiency}% must be between 0% and 100%"
                )
            validated["efficiency_percent"] = efficiency
            
        return validated
    
    @staticmethod
    def validate_grid_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize grid properties"""
        validated = {}
        
        if "connection_status" in properties:
            status = properties["connection_status"]
            if status not in ["connected", "disconnected", "maintenance"]:
                raise HomeStateValidationError(f"Invalid grid connection status: {status}")
            validated["connection_status"] = status
            
        if "sell_energy_kwh" in properties:
            energy = float(properties["sell_energy_kwh"])
            if energy < 0:
                raise HomeStateValidationError("Cannot sell negative energy")
            validated["sell_energy_kwh"] = energy
            
        if "rate_usd_per_kwh" in properties:
            rate = float(properties["rate_usd_per_kwh"])
            if rate < 0:
                raise HomeStateValidationError("Energy rate cannot be negative")
            validated["rate_usd_per_kwh"] = rate
            
        return validated

class HomeStateTool(BaseTool):
    """Base tool for home state operations"""
    name: str = "home_state_tool"
    description: str = "Tool for managing smart home device states"
    home_state_agent: 'HomeStateAgent'
    
    def __init__(self, home_state_agent: 'HomeStateAgent'):
        super().__init__(home_state_agent=home_state_agent)

class ThermostatTool(HomeStateTool):
    """Tool for controlling thermostat"""
    name: str = "thermostat_tool"
    description: str = "Control thermostat temperature, mode, and fan settings. Use this to adjust home temperature."
    
    def _run(self, temperature: Optional[float] = None, mode: Optional[str] = None, fan_mode: Optional[str] = None) -> str:
        """Execute thermostat control"""
        updates = {}
        if temperature is not None:
            updates["target_temperature_f"] = temperature
            updates["temperature_f"] = temperature  # Simulate immediate response
        if mode is not None:
            updates["mode"] = mode
        if fan_mode is not None:
            updates["fan_mode"] = fan_mode
        
        # Validate before updating
        validated_updates = StateValidator.validate_thermostat_properties(updates)
        self.home_state_agent.current_state.update_device(DeviceType.THERMOSTAT, validated_updates)
        return f"Thermostat updated: {validated_updates}"

class BatteryTool(HomeStateTool):
    """Tool for controlling battery/powerwall"""
    name: str = "battery_tool"
    description: str = "Control battery charging, discharging, and backup reserve settings."
    
    def _run(self, soc_percent: Optional[float] = None, backup_reserve: Optional[float] = None, 
             grid_charging: Optional[bool] = None) -> str:
        """Execute battery control"""
        updates = {}
        if soc_percent is not None:
            updates["soc_percent"] = soc_percent
        if backup_reserve is not None:
            updates["backup_reserve_percent"] = backup_reserve
        if grid_charging is not None:
            updates["grid_charging"] = grid_charging
        
        # Validate before updating
        validated_updates = StateValidator.validate_battery_properties(updates)
        self.home_state_agent.current_state.update_device(DeviceType.BATTERY, validated_updates)
        return f"Battery updated: {validated_updates}"


class SolarTool(HomeStateTool):
    """Tool for monitoring and controlling solar panels"""
    name: str = "solar_tool"
    description: str = "Monitor solar panel production and efficiency."
    
    def _run(self, production_kw: Optional[float] = None, efficiency: Optional[float] = None) -> str:
        """Execute solar control"""
        updates = {}
        if production_kw is not None:
            updates["current_production_kw"] = production_kw
        if efficiency is not None:
            updates["efficiency_percent"] = efficiency
        
        # Validate before updating
        validated_updates = StateValidator.validate_solar_properties(updates)
        self.home_state_agent.current_state.update_device(DeviceType.SOLAR, validated_updates)
        return f"Solar system updated: {validated_updates}"


class GridTool(HomeStateTool):
    """Tool for managing grid connection and energy trading"""
    name: str = "grid_tool"
    description: str = "Control grid connection, energy trading, and monitor consumption."
    
    def _run(self, connection_status: Optional[str] = None, sell_energy_kwh: Optional[float] = None,
             rate_usd_per_kwh: Optional[float] = None) -> str:
        """Execute grid operations"""
        updates = {}
        if connection_status is not None:
            updates["connection_status"] = connection_status
        
        # Handle energy selling
        if sell_energy_kwh is not None and rate_usd_per_kwh is not None:
            updates["sell_energy_kwh"] = sell_energy_kwh
            updates["rate_usd_per_kwh"] = rate_usd_per_kwh
        
        # Validate before updating
        validated_updates = StateValidator.validate_grid_properties(updates)
        
        # Process energy selling after validation
        if "sell_energy_kwh" in validated_updates and "rate_usd_per_kwh" in validated_updates:
            profit = validated_updates["sell_energy_kwh"] * validated_updates["rate_usd_per_kwh"]
            self.home_state_agent.current_state.financials.profit_today_usd += profit
            self.home_state_agent.current_state.financials.total_energy_sold_kwh += validated_updates["sell_energy_kwh"]
            validated_updates["energy_sale"] = f"Sold {validated_updates['sell_energy_kwh']} kWh for ${profit:.2f}"
        
        self.home_state_agent.current_state.update_device(DeviceType.GRID, validated_updates)
        return f"Grid operations completed: {validated_updates}"


class HomeStateAgent:
    """
    The Home State Agent (Digital Twin) - Agent 2 in the AURA system.
    
    Functions as a transactional database for the home, maintaining internal state
    and executing batched commands to read or modify device states.
    """
    
    def __init__(self, initial_state_file: Optional[str] = None, openai_api_key: Optional[str] = None):
        self.initial_state_file = initial_state_file or "initial_home_state.json"
        self.current_state: HomeState = self._load_initial_state()
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=openai_api_key
        ) if openai_api_key else None
        
        # Initialize tools
        self.tools = [
            ThermostatTool(self),
            BatteryTool(self),
            SolarTool(self),
            GridTool(self)
        ]
        
        # Create agent if LLM is available
        self.agent_executor = self._create_agent() if self.llm else None
        
        # Memory management
        self._max_state_history = 1000  # Limit state history to prevent memory leaks
        self._state_history: List[HomeState] = []
        self._cleanup_threshold = 0.8  # Cleanup when 80% full
        
    def _load_initial_state(self) -> HomeState:
        """Load initial home state from JSON file"""
        try:
            # Try to load from the backend directory
            state_path = Path(__file__).parent / self.initial_state_file
            if not state_path.exists():
                # Fallback to relative path
                state_path = Path(self.initial_state_file)
            
            with open(state_path, 'r') as f:
                data = json.load(f)
            
            # Convert to HomeState model
            return HomeState(**data)
        except Exception as e:
            print(f"Warning: Could not load initial state from {self.initial_state_file}: {e}")
            # Return default state
            return HomeState(
                metadata=HomeMetadata(
                    home_id="aura-demo-home-01",
                    location="Austin, TX"
                )
            )
    
    def _create_agent(self) -> Optional[AgentExecutor]:
        """Create LangChain agent with tools"""
        if not self.llm:
            return None
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Home State Agent (Digital Twin) for the AURA smart home system.

Your role is to:
1. Maintain the complete state of all home devices (thermostat, battery, solar, grid)
2. Execute batched commands to read or modify device states
3. Ensure state consistency across all operations
4. Return the complete updated home state after each transaction

Available tools:
- thermostat_tool: Control temperature, mode, and fan settings
- battery_tool: Control battery charging, backup reserve, and power flow
- solar_tool: Monitor and control solar panel production
- grid_tool: Manage grid connection and energy trading

Always:
- Execute actions in the order provided
- Maintain state consistency
- Provide clear feedback on what was changed
- Return the complete home state after operations"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    async def process_request(self, request: HomeStateRequest) -> HomeStateResult:
        """
        Process a batched request of actions and return the updated home state.
        This is the main entry point for the Home State Agent.
        """
        start_time = time.time()
        action_results = []
        
        # Process each action in sequence
        for action in request.actions:
            result = await self._execute_action(action)
            action_results.append(result)
            
            # If any action fails, stop processing and return error
            if not result.success:
                processing_time = (time.time() - start_time) * 1000
                return HomeStateResult(
                    success=False,
                    message=f"Action failed: {result.message}",
                    home_state=self.current_state,
                    action_results=action_results,
                    request_id=request.request_id,
                    processing_time_ms=processing_time
                )
        
        # If LangChain agent is available, use it for complex operations
        if self.agent_executor and len(request.actions) > 1:
            # Create a summary of actions for the agent
            action_summary = self._create_action_summary(request.actions)
            try:
                agent_response = await self.agent_executor.ainvoke({
                    "input": f"Execute these home automation actions: {action_summary}"
                })
            except Exception as e:
                # Log warning but don't fail the request
                print(f"Agent execution warning: {e}")
        
        processing_time = (time.time() - start_time) * 1000
        
        # Save state snapshot for history tracking
        self._save_state_snapshot()
        
        return HomeStateResult(
            success=True,
            message=f"Successfully processed {len(request.actions)} actions",
            home_state=self.current_state,
            action_results=action_results,
            request_id=request.request_id,
            processing_time_ms=processing_time
        )
    
    async def _execute_action(self, action: Action) -> ActionResult:
        """Execute a single action on a device"""
        device = self.current_state.get_device(action.device_type)
        previous_value = device.properties.copy() if device else None
        
        # Execute the action based on device type and action type
        if action.device_type == DeviceType.THERMOSTAT:
            await self._execute_thermostat_action(action)
        elif action.device_type == DeviceType.BATTERY:
            await self._execute_battery_action(action)
        elif action.device_type == DeviceType.SOLAR:
            await self._execute_solar_action(action)
        elif action.device_type == DeviceType.GRID:
            await self._execute_grid_action(action)
        else:
            raise DeviceOperationError(f"Unsupported device type: {action.device_type}")
        
        device = self.current_state.get_device(action.device_type)
        new_value = device.properties.copy() if device else None
        
        return ActionResult(
            action=action,
            success=True,
            message=f"Successfully executed {action.action_type} on {action.device_type}",
            previous_value=previous_value,
            new_value=new_value
        )
    
    async def _execute_thermostat_action(self, action: Action):
        """Execute thermostat-specific actions"""
        updates = {}
        
        if action.action_type == ActionType.SET:
            if "temperature" in action.parameters:
                updates["target_temperature_f"] = action.parameters["temperature"]
                updates["temperature_f"] = action.parameters["temperature"]
            if "mode" in action.parameters:
                updates["mode"] = action.parameters["mode"]
        elif action.action_type == ActionType.ADJUST:
            if action.target_value is not None:
                current_temp = self.current_state.get_device(DeviceType.THERMOSTAT).properties.get("temperature_f", 72)
                updates["target_temperature_f"] = action.target_value
                updates["temperature_f"] = action.target_value
        
        if updates:
            # Validate before updating
            validated_updates = StateValidator.validate_thermostat_properties(updates)
            self.current_state.update_device(DeviceType.THERMOSTAT, validated_updates)
    
    async def _execute_battery_action(self, action: Action):
        """Execute battery-specific actions"""
        updates = {}
        
        if action.action_type == ActionType.SET:
            if "soc_percent" in action.parameters:
                updates["soc_percent"] = action.parameters["soc_percent"]
            if "backup_reserve" in action.parameters:
                updates["backup_reserve_percent"] = action.parameters["backup_reserve"]
        elif action.action_type == ActionType.ADJUST:
            if action.target_value is not None:
                updates["soc_percent"] = action.target_value
        
        if updates:
            # Validate before updating
            validated_updates = StateValidator.validate_battery_properties(updates)
            self.current_state.update_device(DeviceType.BATTERY, validated_updates)
    
    async def _execute_solar_action(self, action: Action):
        """Execute solar-specific actions"""
        updates = {}
        
        if action.action_type == ActionType.READ:
            # Reading doesn't change state, just return current values
            pass
        elif action.action_type == ActionType.SET:
            if "production_kw" in action.parameters:
                updates["current_production_kw"] = action.parameters["production_kw"]
        
        if updates:
            # Validate before updating
            validated_updates = StateValidator.validate_solar_properties(updates)
            self.current_state.update_device(DeviceType.SOLAR, validated_updates)
    
    async def _execute_grid_action(self, action: Action):
        """Execute grid-specific actions"""
        updates = {}
        
        if action.action_type == ActionType.SET:
            if "connection_status" in action.parameters:
                updates["connection_status"] = action.parameters["connection_status"]
            if "sell_energy" in action.parameters:
                # Handle energy selling
                energy_kwh = action.parameters["sell_energy"]
                rate = action.parameters.get("rate_usd_per_kwh", 0.83)  # Default rate
                updates["sell_energy_kwh"] = energy_kwh
                updates["rate_usd_per_kwh"] = rate
        
        if updates:
            # Validate before updating
            validated_updates = StateValidator.validate_grid_properties(updates)
            
            # Process energy selling after validation
            if "sell_energy_kwh" in validated_updates and "rate_usd_per_kwh" in validated_updates:
                profit = validated_updates["sell_energy_kwh"] * validated_updates["rate_usd_per_kwh"]
                self.current_state.financials.profit_today_usd += profit
                self.current_state.financials.total_energy_sold_kwh += validated_updates["sell_energy_kwh"]
                validated_updates["last_sale"] = f"Sold {validated_updates['sell_energy_kwh']} kWh for ${profit:.2f}"
            
            self.current_state.update_device(DeviceType.GRID, validated_updates)
    
    def _create_action_summary(self, actions: List[Action]) -> str:
        """Create a human-readable summary of actions for the LangChain agent"""
        summary_parts = []
        for action in actions:
            if action.action_type == ActionType.SET:
                summary_parts.append(f"Set {action.device_type} with {action.parameters}")
            elif action.action_type == ActionType.ADJUST:
                summary_parts.append(f"Adjust {action.device_type} to {action.target_value}")
            elif action.action_type == ActionType.READ:
                summary_parts.append(f"Read {action.device_type} status")
        
        return "; ".join(summary_parts)
    
    def get_current_state(self) -> HomeState:
        """Get the current complete home state"""
        return self.current_state
    
    def reset_to_initial_state(self):
        """Reset home state to initial configuration"""
        self.current_state = self._load_initial_state()
        self._state_history.clear()
    
    def _manage_memory(self):
        """Manage memory by cleaning up old state history"""
        if len(self._state_history) >= self._max_state_history * self._cleanup_threshold:
            # Remove oldest 20% of history
            remove_count = int(self._max_state_history * 0.2)
            self._state_history = self._state_history[remove_count:]
    
    def _save_state_snapshot(self):
        """Save current state as a snapshot for history tracking"""
        # Create a deep copy of current state
        import copy
        state_copy = copy.deepcopy(self.current_state)
        self._state_history.append(state_copy)
        self._manage_memory()
    
    def get_state_history(self, limit: int = 10) -> List[HomeState]:
        """Get recent state history for analysis"""
        return self._state_history[-limit:] if self._state_history else []
    
    def cleanup_resources(self):
        """Clean up resources to prevent memory leaks"""
        self._state_history.clear()
        if self.agent_executor:
            # LangChain agents don't have explicit cleanup, but we can clear references
            self.agent_executor = None
        self.tools.clear()
    
    # async def get_intelligent_recommendations(self, context: str = "") -> str:
    #     """Get intelligent automation recommendations using LangChain"""
    #     if not self.agent_executor:
    #         return "LangChain agent not available for recommendations"
        
    #     try:
    #         # Get recent state history for context
    #         recent_states = self.get_state_history(5)
    #         state_context = self._create_state_context(recent_states)
            
    #         prompt = f"""
    #         Analyze the current home state and provide intelligent recommendations:
            
    #         Current State Context:
    #         {state_context}
            
    #         User Request: {context}
            
    #         Please provide:
    #         1. Energy optimization suggestions
    #         2. Cost-saving opportunities
    #         3. Device coordination recommendations
    #         4. Predictive insights based on patterns
    #         """
            
    #         response = await self.agent_executor.ainvoke({"input": prompt})
    #         return response.get("output", "No recommendations available")
            
    #     except Exception as e:
    #         return f"Error generating recommendations: {str(e)}"
    
    def _create_state_context(self, states: List[HomeState]) -> str:
        """Create a context string from state history"""
        if not states:
            return "No historical data available"
        
        context_parts = []
        for i, state in enumerate(states[-3:]):  # Last 3 states
            context_parts.append(f"State {i+1}:")
            context_parts.append(f"  Thermostat: {state.get_device(DeviceType.THERMOSTAT).properties if state.get_device(DeviceType.THERMOSTAT) else 'N/A'}")
            context_parts.append(f"  Battery SOC: {state.get_device(DeviceType.BATTERY).properties.get('soc_percent', 'N/A') if state.get_device(DeviceType.BATTERY) else 'N/A'}%")
            context_parts.append(f"  Solar Production: {state.get_device(DeviceType.SOLAR).properties.get('current_production_kw', 'N/A') if state.get_device(DeviceType.SOLAR) else 'N/A'}kW")
            context_parts.append(f"  Financials: ${state.financials.profit_today_usd:.2f} profit today")
        
        return "\n".join(context_parts)
    
    async def optimize_energy_usage(self) -> List[Action]:
        """Generate optimized actions based on current state and patterns"""
        if not self.agent_executor:
            return []
        
        try:
            current_state = self.get_current_state()
            battery = current_state.get_device(DeviceType.BATTERY)
            solar = current_state.get_device(DeviceType.SOLAR)
            thermostat = current_state.get_device(DeviceType.THERMOSTAT)
            
            recommendations = []
            
            # Battery optimization based on solar production
            if battery and solar:
                solar_prod = solar.properties.get("current_production_kw", 0)
                battery_soc = battery.properties.get("soc_percent", 0)
                
                if solar_prod > 2.0 and battery_soc < 80:
                    # High solar production, charge battery
                    recommendations.append(create_battery_action(soc_percent=min(100, battery_soc + 20)))
                elif solar_prod < 0.5 and battery_soc > 20:
                    # Low solar, use battery
                    recommendations.append(create_battery_action(soc_percent=max(0, battery_soc - 10)))
            
            # Thermostat optimization for energy savings
            if thermostat:
                current_temp = thermostat.properties.get("temperature_f", 72)
                if current_temp < 68:  # Too cold, heating inefficient
                    recommendations.append(create_thermostat_action(temperature=70))
                elif current_temp > 78:  # Too hot, cooling inefficient
                    recommendations.append(create_thermostat_action(temperature=76))
            
            return recommendations
            
        except Exception as e:
            print(f"Error in energy optimization: {e}")
            return []
    
    async def predict_energy_needs(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Predict energy needs based on historical patterns"""
        try:
            recent_states = self.get_state_history(10)
            if len(recent_states) < 3:
                return {"error": "Insufficient historical data for prediction"}
            
            # Simple pattern analysis (in production, this would use ML models)
            avg_solar_prod = sum(
                state.get_device(DeviceType.SOLAR).properties.get("current_production_kw", 0)
                for state in recent_states
                if state.get_device(DeviceType.SOLAR)
            ) / len(recent_states)
            
            avg_battery_usage = sum(
                state.get_device(DeviceType.BATTERY).properties.get("soc_percent", 0)
                for state in recent_states
                if state.get_device(DeviceType.BATTERY)
            ) / len(recent_states)
            
            prediction = {
                "predicted_solar_production_kw": avg_solar_prod,
                "predicted_battery_soc": avg_battery_usage,
                "confidence": "medium",
                "recommendations": []
            }
            
            if avg_solar_prod > 3.0:
                prediction["recommendations"].append("High solar production expected - consider charging battery")
            elif avg_solar_prod < 1.0:
                prediction["recommendations"].append("Low solar production expected - consider using battery power")
            
            return prediction
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}

    async def generate_intelligent_actions(self, threat_analysis) -> List[Action]:
        """
        Use LLM to intelligently generate home actions based on threat analysis.
        Considers both threat data and current home state for optimal decisions.
        """
        if not self.llm:
            print("⚠️ LLM not available for intelligent action generation")
            print("🔄 Creating fallback action based on threat analysis")
            return self._generate_fallback_action(threat_analysis)
        
        try:
            # Get current home state for context
            current_state = self.get_current_state()
            
            # Build threat context
            threat_context = self._build_threat_context(threat_analysis)
            
            # Build home state context
            home_context = self._build_home_state_context(current_state)
            
            # Create the LLM prompt
            prompt = f"""
You are an intelligent home automation system that generates optimal actions based on threat analysis and current home state.

THREAT ANALYSIS:
{threat_context}

CURRENT HOME STATE:
{home_context}

AVAILABLE DEVICE TYPES AND PARAMETERS:
1. THERMOSTAT:
   - temperature_f: Target temperature (60-90°F)
   - mode: "heat", "cool", "auto", "off"
   - fan_mode: "auto", "on", "circulate"

2. BATTERY:
   - soc_percent: State of charge (0-100%)
   - backup_reserve_percent: Backup reserve (0-100%)
   - grid_charging: True/False

3. SOLAR:
   - current_production_kw: Solar production (0-50 kW)
   - efficiency_percent: Panel efficiency (0-100%)

4. GRID:
   - connection_status: "connected", "disconnected", "maintenance"
   - sell_energy_kwh: Energy to sell (≥0)
   - rate_usd_per_kwh: Selling rate (≥0)

INSTRUCTIONS:
- Analyze the threat level and type
- Consider current home state
- Generate optimal actions for each relevant device
- Prioritize safety and energy efficiency
- Return ONLY valid JSON in the exact format below

OUTPUT FORMAT (JSON):
{{
    "actions": [
        {{
            "device_type": "thermostat|battery|solar|grid",
            "action_type": "set",
            "parameters": {{
                "parameter_name": "value"
            }}
        }}
    ],
    "reasoning": "Brief explanation of the strategy"
}}

Generate actions now:
"""
            
            # Call LLM
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse JSON response
            try:
                # Extract JSON from response (in case LLM adds extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Convert to Action objects
                actions = []
                for action_data in result.get("actions", []):
                    action = Action(
                        device_type=DeviceType(action_data["device_type"]),
                        action_type=ActionType(action_data["action_type"]),
                        parameters=action_data.get("parameters", {})
                    )
                    actions.append(action)
                
                print(f"🤖 LLM generated {len(actions)} intelligent actions")
                print(f"   Reasoning: {result.get('reasoning', 'No reasoning provided')}")
                
                # Ensure at least 1 action is generated
                if not actions:
                    print("⚠️ LLM generated no actions, creating fallback action")
                    actions = self._generate_fallback_action(threat_analysis)
                
                return actions
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"❌ Error parsing LLM response: {e}")
                print(f"   Response: {response_text}")
                print("🔄 Creating fallback action due to parsing error")
                return self._generate_fallback_action(threat_analysis)
                
        except Exception as e:
            print(f"❌ Error in intelligent action generation: {e}")
            print("🔄 Creating fallback action due to execution error")
            return self._generate_fallback_action(threat_analysis)
    
    def _generate_fallback_action(self, threat_analysis) -> List[Action]:
        """
        Generate a fallback action when LLM is unavailable or fails.
        Creates a basic action based on threat level and type.
        """
        actions = []
        
        # Get current state for context
        current_state = self.get_current_state()
        
        # Determine action based on threat level and type
        threat_level = threat_analysis.overall_threat_level
        threat_types = threat_analysis.threat_types
        
        print(f"🔄 Generating fallback action for threat level: {threat_level}")
        print(f"   Threat types: {[t.value for t in threat_types]}")
        
        # Default fallback: Battery backup based on threat level
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            # High/Critical threat - maximize battery backup
            soc_target = 100.0
            backup_reserve = 40.0 if threat_level == ThreatLevel.HIGH else 50.0
        elif threat_level == ThreatLevel.MEDIUM:
            # Medium threat - moderate battery backup
            soc_target = 85.0
            backup_reserve = 30.0
        else:
            # Low threat - minimal battery backup
            soc_target = 75.0
            backup_reserve = 20.0
        
        # Add battery action
        battery_action = Action(
            device_type=DeviceType.BATTERY,
            action_type=ActionType.SET,
            parameters={
                "soc_percent": soc_target,
                "backup_reserve_percent": backup_reserve
            }
        )
        actions.append(battery_action)
        
        # Add threat-specific actions
        if ThreatType.HEAT_WAVE in threat_types:
            # Heat wave - add thermostat action
            temp_target = 70.0 if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] else 72.0
            thermostat_action = Action(
                device_type=DeviceType.THERMOSTAT,
                action_type=ActionType.SET,
                parameters={
                    "temperature_f": temp_target,
                    "mode": "cool"
                }
            )
            actions.append(thermostat_action)
        
        elif ThreatType.GRID_STRAIN in threat_types:
            # Grid strain - prepare for disconnection
            grid_action = Action(
                device_type=DeviceType.GRID,
                action_type=ActionType.SET,
                parameters={
                    "connection_status": "backup_ready"
                }
            )
            actions.append(grid_action)
        
        elif ThreatType.POWER_OUTAGE in threat_types:
            # Power outage - optimize for battery efficiency
            thermostat_action = Action(
                device_type=DeviceType.THERMOSTAT,
                action_type=ActionType.SET,
                parameters={
                    "temperature_f": 70.0,
                    "mode": "cool"
                }
            )
            actions.append(thermostat_action)
        
        elif ThreatType.ENERGY_SHORTAGE in threat_types:
            # Energy shortage - sell excess energy
            grid_action = Action(
                device_type=DeviceType.GRID,
                action_type=ActionType.SET,
                parameters={
                    "sell_energy_kwh": 3.0,
                    "rate_usd_per_kwh": 1.0
                }
            )
            actions.append(grid_action)
        
        print(f"🔄 Generated {len(actions)} fallback actions")
        for i, action in enumerate(actions, 1):
            print(f"   {i}. {action.device_type.value.upper()}: {action.action_type.value} - {action.parameters}")
        
        return actions
    
    def _build_threat_context(self, threat_analysis) -> str:
        """Build context string from threat analysis"""
        context_parts = []
        
        context_parts.append(f"Overall Threat Level: {threat_analysis.overall_threat_level}")
        context_parts.append(f"Threat Types: {[t.value for t in threat_analysis.threat_types]}")
        context_parts.append(f"Confidence Score: {threat_analysis.confidence_score:.2f}")
        context_parts.append(f"Risk Score: {threat_analysis.risk_score:.2f}")
        
        if threat_analysis.indicators:
            context_parts.append("Key Indicators:")
            for indicator in threat_analysis.indicators:
                context_parts.append(f"  • {indicator.indicator_type}: {indicator.value} - {indicator.description}")
        
        return "\n".join(context_parts)
    
    def _build_home_state_context(self, home_state: HomeState) -> str:
        """Build context string from current home state"""
        context_parts = []
        
        for device_type in [DeviceType.THERMOSTAT, DeviceType.BATTERY, DeviceType.SOLAR, DeviceType.GRID]:
            device = home_state.get_device(device_type)
            if device:
                context_parts.append(f"{device_type.value.upper()}: {device.properties}")
        
        context_parts.append(f"Financials: ${home_state.financials.profit_today_usd:.2f} profit today")
        
        return "\n".join(context_parts)


# Convenience functions for creating common actions
def create_thermostat_action(temperature: float = None, mode: str = None) -> Action:
    """Create a thermostat control action"""
    params = {}
    if temperature is not None:
        params["temperature"] = temperature
    if mode is not None:
        params["mode"] = mode
    
    return Action(
        device_type=DeviceType.THERMOSTAT,
        action_type=ActionType.SET,
        parameters=params
    )

def create_battery_action(soc_percent: float = None, backup_reserve: float = None) -> Action:
    """Create a battery control action"""
    params = {}
    if soc_percent is not None:
        params["soc_percent"] = soc_percent
    if backup_reserve is not None:
        params["backup_reserve"] = backup_reserve
    
    return Action(
        device_type=DeviceType.BATTERY,
        action_type=ActionType.SET,
        parameters=params
    )


def create_energy_sale_action(energy_kwh: float, rate_usd_per_kwh: float = 0.83) -> Action:
    """Create an energy sale action"""
    return Action(
        device_type=DeviceType.GRID,
        action_type=ActionType.SET,
        parameters={
            "sell_energy": energy_kwh,
            "rate_usd_per_kwh": rate_usd_per_kwh
        }
    )

# Update forward references for Pydantic models
HomeStateTool.update_forward_refs()
ThermostatTool.update_forward_refs()
BatteryTool.update_forward_refs()
GridTool.update_forward_refs()
SolarTool.update_forward_refs()
