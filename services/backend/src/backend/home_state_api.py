import os
from typing import Optional
from fastapi import APIRouter, HTTPException
from datetime import datetime

from .home_state_agent import HomeStateAgent
from .home_state_models import (
    HomeStateRequest, HomeStateResult, Action, DeviceType, ActionType,
    create_thermostat_action, create_battery_action, create_energy_sale_action
)

# Initialize the Home State Agent
home_state_agent: Optional[HomeStateAgent] = None

def initialize_home_state_agent():
    """Initialize the Home State Agent with OpenAI API key if available"""
    global home_state_agent
    openai_api_key = os.getenv("OPENAI_API_KEY")
    home_state_agent = HomeStateAgent(openai_api_key=openai_api_key)
    return home_state_agent

# Create FastAPI router
router = APIRouter(prefix="/home-state", tags=["Home State Agent"])

@router.on_event("startup")
async def startup_home_state_agent():
    """Initialize the Home State Agent on startup"""
    initialize_home_state_agent()
    print("✅ Home State Agent (Digital Twin) initialized")

@router.post("/execute", response_model=HomeStateResult)
async def execute_home_actions(request: HomeStateRequest):
    """
    Execute a batch of actions on home devices and return the updated state.
    This is the main API endpoint for the Home State Agent.
    """
    if not home_state_agent:
        raise HTTPException(status_code=500, detail="Home State Agent not initialized")
    
    try:
        result = await home_state_agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute actions: {str(e)}")

@router.get("/status")
async def get_home_status():
    """Get the current complete home state"""
    if not home_state_agent:
        raise HTTPException(status_code=500, detail="Home State Agent not initialized")
    
    current_state = home_state_agent.get_current_state()
    return {
        "success": True,
        "home_state": current_state,
        "timestamp": datetime.utcnow()
    }

@router.post("/reset")
async def reset_home_state():
    """Reset home state to initial configuration"""
    if not home_state_agent:
        raise HTTPException(status_code=500, detail="Home State Agent not initialized")
    
    home_state_agent.reset_to_initial_state()
    return {
        "success": True,
        "message": "Home state reset to initial configuration",
        "timestamp": datetime.utcnow()
    }

@router.post("/emergency-prep")
async def emergency_preparation():
    """
    Execute emergency preparation sequence (pre-cool, charge battery, prepare for grid disconnect)
    This is a convenience endpoint that executes multiple actions for emergency scenarios.
    """
    if not home_state_agent:
        raise HTTPException(status_code=500, detail="Home State Agent not initialized")
    
    # Create emergency preparation actions
    actions = [
        create_thermostat_action(temperature=68.0, mode="cool"),  # Pre-cool to 68°F
        create_battery_action(soc_percent=100.0, backup_reserve=20.0),  # Charge to 100%
        Action(
            device_type=DeviceType.GRID,
            action_type=ActionType.SET,
            parameters={"connection_status": "backup_ready"}
        )
    ]
    
    request = HomeStateRequest(
        actions=actions,
        request_id=f"emergency_prep_{int(datetime.utcnow().timestamp())}"
    )
    
    try:
        result = await home_state_agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute emergency preparation: {str(e)}")

@router.post("/energy-sale")
async def execute_energy_sale(energy_kwh: float, rate_usd_per_kwh: float = 0.83):
    """
    Execute an energy sale to the grid
    """
    if not home_state_agent:
        raise HTTPException(status_code=500, detail="Home State Agent not initialized")
    
    if energy_kwh <= 0:
        raise HTTPException(status_code=400, detail="Energy amount must be positive")
    
    actions = [create_energy_sale_action(energy_kwh, rate_usd_per_kwh)]
    
    request = HomeStateRequest(
        actions=actions,
        request_id=f"energy_sale_{int(datetime.utcnow().timestamp())}"
    )
    
    try:
        result = await home_state_agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute energy sale: {str(e)}")

@router.post("/thermostat/set")
async def set_thermostat(temperature: float, mode: str = "cool"):
    """Set thermostat temperature and mode"""
    if not home_state_agent:
        raise HTTPException(status_code=500, detail="Home State Agent not initialized")
    
    if not (60 <= temperature <= 85):
        raise HTTPException(status_code=400, detail="Temperature must be between 60°F and 85°F")
    
    actions = [create_thermostat_action(temperature=temperature, mode=mode)]
    
    request = HomeStateRequest(
        actions=actions,
        request_id=f"thermostat_{int(datetime.utcnow().timestamp())}"
    )
    
    try:
        result = await home_state_agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set thermostat: {str(e)}")

@router.post("/battery/charge")
async def charge_battery(target_soc: float, backup_reserve: Optional[float] = None):
    """Charge battery to target state of charge"""
    if not home_state_agent:
        raise HTTPException(status_code=500, detail="Home State Agent not initialized")
    
    if not (0 <= target_soc <= 100):
        raise HTTPException(status_code=400, detail="Battery SOC must be between 0% and 100%")
    
    actions = [create_battery_action(soc_percent=target_soc, backup_reserve=backup_reserve)]
    
    request = HomeStateRequest(
        actions=actions,
        request_id=f"battery_charge_{int(datetime.utcnow().timestamp())}"
    )
    
    try:
        result = await home_state_agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to charge battery: {str(e)}")

# Export the router and agent for use in main app
__all__ = ["router", "home_state_agent", "initialize_home_state_agent"]
