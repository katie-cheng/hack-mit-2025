import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from .threat_assessment_agent import ThreatAssessmentAgent
from .threat_models import (
    ThreatAnalysisRequest, ThreatAnalysisResult, MockDataConfig, DataSourceStatus
)

# Initialize the Threat Assessment Agent
threat_assessment_agent: Optional[ThreatAssessmentAgent] = None

def initialize_threat_assessment_agent():
    """Initialize the Threat Assessment Agent with API keys and configuration"""
    global threat_assessment_agent
    
    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Configure mock data usage
    mock_config = MockDataConfig(
        use_mock_weather=os.getenv("USE_MOCK_WEATHER", "true").lower() == "true",
        use_mock_grid=os.getenv("USE_MOCK_GRID", "true").lower() == "true",
        mock_weather_file=os.getenv("MOCK_WEATHER_FILE", "mock_weather_data.json"),
        mock_grid_file=os.getenv("MOCK_GRID_FILE", "mock_grid_data.json")
    )
    
    threat_assessment_agent = ThreatAssessmentAgent(
        openai_api_key=openai_api_key,
        mock_config=mock_config
    )
    return threat_assessment_agent

# Create FastAPI router
router = APIRouter(prefix="/threat-assessment", tags=["Threat Assessment Agent"])

@router.on_event("startup")
async def startup_threat_assessment_agent():
    """Initialize the Threat Assessment Agent on startup"""
    initialize_threat_assessment_agent()
    print("✅ Threat Assessment Agent (The Oracle) initialized")

@router.post("/analyze", response_model=ThreatAnalysisResult)
async def analyze_threats(request: ThreatAnalysisRequest):
    """
    Analyze threats for a given location.
    This is the main API endpoint for the Threat Assessment Agent.
    """
    if not threat_assessment_agent:
        raise HTTPException(status_code=500, detail="Threat Assessment Agent not initialized")
    
    try:
        result = await threat_assessment_agent.analyze_threats(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze threats: {str(e)}")

@router.get("/analyze/{location}")
async def analyze_threats_simple(
    location: str,
    include_weather: bool = Query(True, description="Include weather data analysis"),
    include_grid: bool = Query(True, description="Include grid data analysis"),
    include_research: bool = Query(False, description="Include Perplexity research")
):
    """
    Simplified threat analysis endpoint with query parameters.
    """
    if not threat_assessment_agent:
        raise HTTPException(status_code=500, detail="Threat Assessment Agent not initialized")
    
    request = ThreatAnalysisRequest(
        location=location,
        include_weather=include_weather,
        include_grid=include_grid,
        include_research=include_research,
        request_id=f"simple_{int(datetime.utcnow().timestamp())}"
    )
    
    try:
        result = await threat_assessment_agent.analyze_threats(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze threats: {str(e)}")

@router.get("/status")
async def get_agent_status():
    """Get the current status of the Threat Assessment Agent and data sources"""
    if not threat_assessment_agent:
        raise HTTPException(status_code=500, detail="Threat Assessment Agent not initialized")
    
    data_source_status = threat_assessment_agent.get_data_source_status()
    
    return {
        "success": True,
        "agent_status": "active",
        "data_sources": data_source_status,
        "timestamp": datetime.utcnow()
    }

@router.post("/config/mock")
async def update_mock_config(
    use_mock_weather: bool = Query(True, description="Use mock weather data"),
    use_mock_grid: bool = Query(True, description="Use mock grid data"),
    mock_weather_file: str = Query("mock_weather_data.json", description="Mock weather file"),
    mock_grid_file: str = Query("mock_grid_data.json", description="Mock grid file")
):
    """Update mock data configuration"""
    if not threat_assessment_agent:
        raise HTTPException(status_code=500, detail="Threat Assessment Agent not initialized")
    
    config = MockDataConfig(
        use_mock_weather=use_mock_weather,
        use_mock_grid=use_mock_grid,
        mock_weather_file=mock_weather_file,
        mock_grid_file=mock_grid_file
    )
    
    threat_assessment_agent.update_mock_config(config)
    
    return {
        "success": True,
        "message": "Mock configuration updated",
        "config": config.dict(),
        "timestamp": datetime.utcnow()
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "Threat Assessment Agent (The Oracle)",
        "timestamp": datetime.utcnow()
    }

@router.post("/test/austin")
async def test_austin_analysis():
    """
    Test endpoint for Austin, TX analysis using mock data.
    Useful for testing the complete pipeline.
    """
    if not threat_assessment_agent:
        raise HTTPException(status_code=500, detail="Threat Assessment Agent not initialized")
    
    request = ThreatAnalysisRequest(
        location="Austin, TX",
        include_weather=True,
        include_grid=True,
        include_research=False,  # Skip research for faster testing
        request_id=f"test_austin_{int(datetime.utcnow().timestamp())}"
    )
    
    try:
        result = await threat_assessment_agent.analyze_threats(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test analysis failed: {str(e)}")

@router.post("/test/heatwave")
async def test_heatwave_scenario():
    """
    Test endpoint for heatwave scenario analysis.
    This will use mock data that simulates extreme heat conditions.
    """
    if not threat_assessment_agent:
        raise HTTPException(status_code=500, detail="Threat Assessment Agent not initialized")
    
    # Ensure we're using mock data for this test
    config = MockDataConfig(
        use_mock_weather=True,
        use_mock_grid=True,
        mock_weather_file="mock_weather_data.json",
        mock_grid_file="mock_grid_data.json"
    )
    threat_assessment_agent.update_mock_config(config)
    
    request = ThreatAnalysisRequest(
        location="Austin, TX",
        include_weather=True,
        include_grid=True,
        include_research=False,
        request_id=f"test_heatwave_{int(datetime.utcnow().timestamp())}"
    )
    
    try:
        result = await threat_assessment_agent.analyze_threats(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatwave test failed: {str(e)}")

# Export the router and agent for use in main app
__all__ = ["router", "threat_assessment_agent", "initialize_threat_assessment_agent"]
