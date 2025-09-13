"""
Main entry point for AURA Smart Home Management Agent on FetchAI AgentVerse
"""

import os
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from src.aura_agent import AURAAgent
from src.aura_agent.models import (
    HomeStatus, Homeowner, VoiceCallRequest, VoiceCallResponse,
    SimulationRequest, SimulationResponse, AgentResponse
)


# Load environment variables
load_dotenv()

# Global agent instance
aura_agent: AURAAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global aura_agent
    
    # Startup
    print("🚀 Starting AURA Smart Home Management Agent...")
    aura_agent = AURAAgent(name="AURA")
    print("✅ AURA Agent initialized successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AURA Agent...")


# Create FastAPI app
app = FastAPI(
    title="AURA Smart Home Management Agent",
    description="AI-powered smart home management agent for FetchAI AgentVerse",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AURA Smart Home Management Agent",
        "version": "1.0.0",
        "status": "running",
        "agentverse": "enabled"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "AURA",
        "services": {
            "voice_service": "active" if aura_agent.voice_service else "inactive",
            "simulator": "active" if aura_agent.simulator else "inactive",
            "homeowners": len(aura_agent.registered_homeowners)
        }
    }


@app.post("/register", response_model=AgentResponse)
async def register_homeowner(name: str, phone_number: str):
    """Register a new homeowner"""
    try:
        result = await aura_agent.register_homeowner(name, phone_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/homeowners", response_model=AgentResponse)
async def get_homeowners():
    """Get registered homeowners"""
    try:
        result = await aura_agent.get_registered_homeowners()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/home-status", response_model=AgentResponse)
async def get_home_status():
    """Get current home status"""
    try:
        result = await aura_agent.get_home_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate-heatwave", response_model=AgentResponse)
async def simulate_heatwave():
    """Simulate heatwave response"""
    try:
        result = await aura_agent.simulate_heatwave()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulation/reset", response_model=AgentResponse)
async def reset_simulation():
    """Reset simulation state"""
    try:
        result = await aura_agent.reset_simulation()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice-call", response_model=VoiceCallResponse)
async def make_voice_call(request: VoiceCallRequest):
    """Make a voice call"""
    try:
        if request.call_type == "warning":
            result = aura_agent.voice_service.send_warning_call(request.phone_number)
        elif request.call_type == "resolution":
            result = aura_agent.voice_service.send_resolution_call(request.phone_number)
        else:
            raise HTTPException(status_code=400, detail="Invalid call type")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AgentVerse specific endpoints
@app.post("/agentverse/message")
async def handle_agentverse_message(message: dict):
    """Handle messages from AgentVerse platform"""
    try:
        from src.aura_agent.aura_agent import Message as AgentMessage
        
        # Convert AgentVerse message to internal format
        agent_message = AgentMessage(
            content=message.get("content", ""),
            source=message.get("source", "agentverse"),
            target=message.get("target", "AURA")
        )
        
        # Process message through agent
        response = await aura_agent.handle_message(agent_message)
        
        return {
            "success": True,
            "response": response.content,
            "source": response.source,
            "target": response.target
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agentverse/capabilities")
async def get_agent_capabilities():
    """Get agent capabilities for AgentVerse"""
    return {
        "agent_id": os.getenv("AGENTVERSE_AGENT_ID", "aura-agent"),
        "name": "AURA",
        "description": "Smart Home Management Agent",
        "capabilities": [
            "voice_calls",
            "smart_home_control", 
            "weather_monitoring",
            "energy_management",
            "homeowner_registration"
        ],
        "endpoints": [
            "/register",
            "/homeowners", 
            "/home-status",
            "/simulate-heatwave",
            "/simulation/reset",
            "/voice-call",
            "/agentverse/message"
        ]
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
