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

from home_state_models import (
    HomeStateRequest, HomeStateResult, HomeState, Action, ActionResult,
    DeviceType, ActionType, DeviceState, HomeMetadata, FinancialData
)


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
        try:
            updates = {}
            if temperature is not None:
                updates["target_temperature_f"] = temperature
                updates["temperature_f"] = temperature  # Simulate immediate response
            if mode is not None:
                updates["mode"] = mode
            if fan_mode is not None:
                updates["fan_mode"] = fan_mode
            
            self.home_state_agent.current_state.update_device(DeviceType.THERMOSTAT, updates)
            return f"Thermostat updated: {updates}"
        except Exception as e:
            return f"Error updating thermostat: {str(e)}"


class BatteryTool(HomeStateTool):
    """Tool for controlling battery/powerwall"""
    name: str = "battery_tool"
    description: str = "Control battery charging, discharging, and backup reserve settings."
    
    def _run(self, soc_percent: Optional[float] = None, backup_reserve: Optional[float] = None, 
             grid_charging: Optional[bool] = None) -> str:
        """Execute battery control"""
        try:
            updates = {}
            if soc_percent is not None:
                updates["soc_percent"] = min(100, max(0, soc_percent))
            if backup_reserve is not None:
                updates["backup_reserve_percent"] = min(100, max(0, backup_reserve))
            if grid_charging is not None:
                updates["grid_charging"] = grid_charging
            
            self.home_state_agent.current_state.update_device(DeviceType.BATTERY, updates)
            return f"Battery updated: {updates}"
        except Exception as e:
            return f"Error updating battery: {str(e)}"


class SolarTool(HomeStateTool):
    """Tool for monitoring and controlling solar panels"""
    name: str = "solar_tool"
    description: str = "Monitor solar panel production and efficiency."
    
    def _run(self, production_kw: Optional[float] = None, efficiency: Optional[float] = None) -> str:
        """Execute solar control"""
        try:
            updates = {}
            if production_kw is not None:
                updates["current_production_kw"] = max(0, production_kw)
            if efficiency is not None:
                updates["efficiency_percent"] = min(100, max(0, efficiency))
            
            self.home_state_agent.current_state.update_device(DeviceType.SOLAR, updates)
            return f"Solar system updated: {updates}"
        except Exception as e:
            return f"Error updating solar: {str(e)}"


class GridTool(HomeStateTool):
    """Tool for managing grid connection and energy trading"""
    name: str = "grid_tool"
    description: str = "Control grid connection, energy trading, and monitor consumption."
    
    def _run(self, connection_status: Optional[str] = None, sell_energy_kwh: Optional[float] = None,
             rate_usd_per_kwh: Optional[float] = None) -> str:
        """Execute grid operations"""
        try:
            updates = {}
            if connection_status is not None:
                updates["connection_status"] = connection_status
            
            # Handle energy selling
            if sell_energy_kwh is not None and rate_usd_per_kwh is not None:
                profit = sell_energy_kwh * rate_usd_per_kwh
                self.home_state_agent.current_state.financials.profit_today_usd += profit
                self.home_state_agent.current_state.financials.total_energy_sold_kwh += sell_energy_kwh
                updates["energy_sale"] = f"Sold {sell_energy_kwh} kWh for ${profit:.2f}"
            
            self.home_state_agent.current_state.update_device(DeviceType.GRID, updates)
            return f"Grid operations completed: {updates}"
        except Exception as e:
            return f"Error with grid operations: {str(e)}"


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
        
        try:
            # Process each action in sequence
            for action in request.actions:
                result = await self._execute_action(action)
                action_results.append(result)
            
            # If LangChain agent is available, use it for complex operations
            if self.agent_executor and len(request.actions) > 1:
                # Create a summary of actions for the agent
                action_summary = self._create_action_summary(request.actions)
                try:
                    agent_response = await self.agent_executor.ainvoke({
                        "input": f"Execute these home automation actions: {action_summary}"
                    })
                except Exception as e:
                    print(f"Agent execution warning: {e}")
            
            processing_time = (time.time() - start_time) * 1000
            
            return HomeStateResult(
                success=True,
                message=f"Successfully processed {len(request.actions)} actions",
                home_state=self.current_state,
                action_results=action_results,
                request_id=request.request_id,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return HomeStateResult(
                success=False,
                message=f"Error processing request: {str(e)}",
                home_state=self.current_state,
                action_results=action_results,
                request_id=request.request_id,
                processing_time_ms=processing_time
            )
    
    async def _execute_action(self, action: Action) -> ActionResult:
        """Execute a single action on a device"""
        try:
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
            
            device = self.current_state.get_device(action.device_type)
            new_value = device.properties.copy() if device else None
            
            return ActionResult(
                action=action,
                success=True,
                message=f"Successfully executed {action.action_type} on {action.device_type}",
                previous_value=previous_value,
                new_value=new_value
            )
            
        except Exception as e:
            return ActionResult(
                action=action,
                success=False,
                message=f"Failed to execute action: {str(e)}",
                previous_value=None,
                new_value=None
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
            self.current_state.update_device(DeviceType.THERMOSTAT, updates)
    
    async def _execute_battery_action(self, action: Action):
        """Execute battery-specific actions"""
        updates = {}
        
        if action.action_type == ActionType.SET:
            if "soc_percent" in action.parameters:
                updates["soc_percent"] = min(100, max(0, action.parameters["soc_percent"]))
            if "backup_reserve" in action.parameters:
                updates["backup_reserve_percent"] = action.parameters["backup_reserve"]
        elif action.action_type == ActionType.ADJUST:
            if action.target_value is not None:
                updates["soc_percent"] = min(100, max(0, action.target_value))
        
        if updates:
            self.current_state.update_device(DeviceType.BATTERY, updates)
    
    async def _execute_solar_action(self, action: Action):
        """Execute solar-specific actions"""
        updates = {}
        
        if action.action_type == ActionType.READ:
            # Reading doesn't change state, just return current values
            pass
        elif action.action_type == ActionType.SET:
            if "production_kw" in action.parameters:
                updates["current_production_kw"] = max(0, action.parameters["production_kw"])
        
        if updates:
            self.current_state.update_device(DeviceType.SOLAR, updates)
    
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
                profit = energy_kwh * rate
                
                self.current_state.financials.profit_today_usd += profit
                self.current_state.financials.total_energy_sold_kwh += energy_kwh
                updates["last_sale"] = f"Sold {energy_kwh} kWh for ${profit:.2f}"
        
        if updates:
            self.current_state.update_device(DeviceType.GRID, updates)
    
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
