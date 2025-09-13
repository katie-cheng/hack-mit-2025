import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from datetime import datetime

from .agent_orchestrator import orchestrator
from .threat_models import ThreatAnalysisRequest
from .home_state_models import HomeStateRequest, Action, DeviceType, ActionType

# Create FastAPI router
router = APIRouter(prefix="/aura", tags=["AURA Integration"])

@router.on_event("startup")
async def startup_integration():
    """Initialize the AURA integration system"""
    await orchestrator.initialize()
    print("✅ AURA Integration System initialized")

@router.post("/threat-to-action")
async def execute_threat_to_action_pipeline(
    location: str = Query(..., description="Location to analyze and protect"),
    include_research: bool = Query(False, description="Include Perplexity research"),
    scenario: str = Query("heatwave", description="Scenario: heatwave, normal, storm, outage")
):
    """
    Execute the complete AURA threat-to-action pipeline.
    
    This is the main endpoint that:
    1. Analyzes environmental threats for the location
    2. Generates appropriate home protection actions
    3. Executes those actions on the home state
    4. Returns complete results
    """
    try:
        # Configure mock data based on scenario
        await _configure_scenario(scenario)
        
        # Execute the complete pipeline
        result = await orchestrator.process_threat_to_action(
            location=location,
            include_research=include_research
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@router.get("/scenarios")
async def get_available_scenarios():
    """Get available threat scenarios for testing"""
    return {
        "scenarios": [
            {
                "id": "heatwave",
                "name": "Extreme Heat Wave",
                "description": "Dangerous heat with grid strain - triggers emergency cooling and battery charging",
                "weather_file": "mock_weather_data.json",
                "grid_file": "mock_grid_data.json"
            },
            {
                "id": "normal",
                "name": "Normal Conditions",
                "description": "Typical weather and grid conditions - minimal actions required",
                "weather_file": "mock_weather_normal.json",
                "grid_file": "mock_grid_normal.json"
            },
            {
                "id": "storm",
                "name": "Severe Thunderstorm",
                "description": "Severe weather with power outage risk - prepares for backup power",
                "weather_file": "mock_weather_storm.json",
                "grid_file": "mock_grid_data.json"
            },
            {
                "id": "outage",
                "name": "Grid Outage",
                "description": "Active power outage - maximizes battery backup and conservation",
                "weather_file": "mock_weather_storm.json",
                "grid_file": "mock_grid_outage.json"
            }
        ]
    }

@router.post("/scenarios/{scenario_id}/execute")
async def execute_scenario(
    scenario_id: str,
    location: str = Query("Austin, TX", description="Location for the scenario"),
    include_research: bool = Query(False, description="Include Perplexity research")
):
    """Execute a specific threat scenario"""
    try:
        # Configure mock data for the scenario
        await _configure_scenario(scenario_id)
        
        # Execute the pipeline
        result = await orchestrator.process_threat_to_action(
            location=location,
            include_research=include_research
        )
        
        return {
            "scenario": scenario_id,
            "location": location,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario execution failed: {str(e)}")

@router.get("/status")
async def get_system_status():
    """Get complete AURA system status"""
    try:
        status = await orchestrator.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.post("/reset")
async def reset_system():
    """Reset the entire AURA system to initial state"""
    try:
        await orchestrator.reset_system()
        return {
            "success": True,
            "message": "AURA system reset to initial state",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System reset failed: {str(e)}")

@router.get("/home-state")
async def get_current_home_state():
    """Get current home state from the Digital Twin"""
    try:
        home_state = orchestrator.home_agent.get_current_state()
        return {
            "success": True,
            "home_state": home_state,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get home state: {str(e)}")

@router.post("/emergency-prep")
async def emergency_preparation():
    """
    Execute emergency preparation sequence.
    This is a quick action for immediate threat response.
    """
    try:
        # Create emergency actions
        emergency_actions = [
            Action(
                device_type=DeviceType.THERMOSTAT,
                action_type=ActionType.SET,
                parameters={"temperature": 68.0, "mode": "cool"}
            ),
            Action(
                device_type=DeviceType.BATTERY,
                action_type=ActionType.SET,
                parameters={"soc_percent": 100.0, "backup_reserve": 30.0}
            ),
            Action(
                device_type=DeviceType.GRID,
                action_type=ActionType.SET,
                parameters={"connection_status": "backup_ready"}
            )
        ]
        
        request = HomeStateRequest(
            actions=emergency_actions,
            request_id=f"emergency_prep_{int(datetime.utcnow().timestamp())}"
        )
        
        result = await orchestrator.home_agent.process_request(request)
        
        return {
            "success": True,
            "message": "Emergency preparation completed",
            "home_state": result.home_state,
            "actions_executed": len(emergency_actions),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency preparation failed: {str(e)}")

@router.get("/threat-mapping")
async def get_threat_action_mapping():
    """Get the current threat-to-action mapping rules"""
    try:
        mapping = orchestrator.get_threat_action_mapping()
        return {
            "success": True,
            "mapping": mapping,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat mapping: {str(e)}")

@router.post("/threat-mapping/{threat_type}")
async def update_threat_mapping(
    threat_type: str,
    actions: list
):
    """Update threat-to-action mapping for a specific threat type"""
    try:
        orchestrator.update_threat_action_mapping(threat_type, actions)
        return {
            "success": True,
            "message": f"Updated threat mapping for {threat_type}",
            "threat_type": threat_type,
            "actions_count": len(actions),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update threat mapping: {str(e)}")

@router.get("/health")
async def health_check():
    """Comprehensive health check for the AURA system"""
    try:
        status = await orchestrator.get_system_status()
        
        return {
            "status": "healthy",
            "system": "AURA Smart Home Management",
            "agents": {
                "threat_assessment": "active",
                "home_state": "active",
                "orchestrator": "active"
            },
            "timestamp": datetime.utcnow(),
            "details": status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }


async def _configure_scenario(scenario: str):
    """Configure mock data based on scenario"""
    scenario_configs = {
        "heatwave": {
            "weather_file": "mock_weather_data.json",
            "grid_file": "mock_grid_data.json"
        },
        "normal": {
            "weather_file": "mock_weather_normal.json",
            "grid_file": "mock_grid_normal.json"
        },
        "storm": {
            "weather_file": "mock_weather_storm.json",
            "grid_file": "mock_grid_data.json"
        },
        "outage": {
            "weather_file": "mock_weather_storm.json",
            "grid_file": "mock_grid_outage.json"
        }
    }
    
    if scenario in scenario_configs:
        config = scenario_configs[scenario]
        orchestrator.threat_agent.update_mock_config({
            "use_mock_weather": True,
            "use_mock_grid": True,
            "mock_weather_file": config["weather_file"],
            "mock_grid_file": config["grid_file"]
        })
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


# Export the router
__all__ = ["router"]
