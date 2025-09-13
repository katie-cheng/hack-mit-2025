import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    HomeownerRegistration, RegisteredHomeowner, RegistrationResponse,
    SmartHomeAlert, AlertResponse, HomeStatus, HomeStatusResponse,
    SimulationRequest, WeatherEvent
)
from .voice_alerts import AURAVoiceService
from .smart_home_simulator import SmartHomeSimulator

# Load environment variables from multiple locations
load_dotenv()  # Load from backend/.env
load_dotenv("../../.env.local")  # Load from root .env.local

app = FastAPI(title="AURA Smart Home Management API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# In-memory storage
registered_homeowners: Dict[str, RegisteredHomeowner] = {}
home_status: HomeStatus = HomeStatus(
    battery_level=45.0,
    thermostat_temp=72.0,
    market_status="monitoring",
    energy_sold=0.0,
    profit_generated=0.0,
    solar_charging=False,
    ac_running=False,
    last_updated=datetime.utcnow()
)

# Initialize services
voice_service: Optional[AURAVoiceService] = None
simulator: Optional[SmartHomeSimulator] = None


@app.on_event("startup")
async def startup_event():
    global voice_service, simulator
    try:
        voice_service = AURAVoiceService()
        simulator = SmartHomeSimulator(home_status_ref=home_status)
        print("✅ AURA services initialized successfully")
    except ValueError as e:
        print(f"❌ Service initialization failed: {e}")


@app.get("/")
async def root():
    return {"message": "AURA Smart Home Management API", "status": "running"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "registered_homeowners": len(registered_homeowners),
        "voice_service": voice_service is not None,
        "simulator": simulator is not None,
        "home_status": {
            "battery_level": home_status.battery_level,
            "thermostat_temp": home_status.thermostat_temp,
            "market_status": home_status.market_status,
        }
    }

@app.post("/register", response_model=RegistrationResponse)
async def register_homeowner(registration: HomeownerRegistration):
    """
    Register a new homeowner for AURA smart home management
    """
    try:
        # Check if phone number already exists
        for homeowner in registered_homeowners.values():
            if homeowner.phone_number == registration.phone_number:
                raise HTTPException(status_code=400, detail="Phone number already registered")
        
        # Create new homeowner
        homeowner_id = str(uuid.uuid4())
        
        registered_homeowner = RegisteredHomeowner(
            id=homeowner_id,
            name=registration.name,
            phone_number=registration.phone_number,
            registered_at=datetime.utcnow()
        )
        
        # Store in memory
        registered_homeowners[homeowner_id] = registered_homeowner
        
        return RegistrationResponse(
            success=True,
            message=f"Homeowner {registration.name} registered successfully",
            homeowner_id=homeowner_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/homeowners")
async def list_homeowners():
    """
    Get all registered homeowners for AURA dashboard
    """
    return {
        "total_homeowners": len(registered_homeowners),
        "homeowners": [
            {
                "id": homeowner.id,
                "name": homeowner.name,
                "phone_number": homeowner.phone_number,
                "registered_at": homeowner.registered_at.isoformat()
            }
            for homeowner in registered_homeowners.values()
        ]
    }

@app.get("/home-status", response_model=HomeStatusResponse)
async def get_home_status():
    """
    Get current smart home status for dashboard
    """
    return HomeStatusResponse(
        success=True,
        status=home_status,
        message="Home status retrieved successfully"
    )

@app.post("/simulate-heatwave", response_model=AlertResponse)
async def simulate_heatwave(background_tasks: BackgroundTasks):
    """
    Simulate a heatwave event and initiate the AURA response sequence
    """
    try:
        if not voice_service or not simulator:
            raise HTTPException(
                status_code=500,
                detail="AURA services not available",
            )

        # Create heatwave weather event
        weather_event = WeatherEvent(
            event_type="heatwave",
            probability=92.0,
            severity="high",
            predicted_time="4:00 PM today",
            description="Grid-straining heatwave event detected"
        )

        # Create warning alert
        warning_alert = SmartHomeAlert(
            alert_type="warning",
            weather_event=weather_event,
            message="Our analyst agents have detected a 92% probability of a grid-straining heatwave event at 4 pm today. Would you like us to prepare your home?",
            action_required=True
        )

        # Get all homeowner phone numbers
        phone_numbers = [homeowner.phone_number for homeowner in registered_homeowners.values()]
        
        if not phone_numbers:
            raise HTTPException(status_code=400, detail="No homeowners registered")

        # Initiate warning call
        call_result = await voice_service.send_warning_call(warning_alert, phone_numbers[0])
        
        # Start background simulation
        background_tasks.add_task(simulator.simulate_heatwave_response)
        
        return AlertResponse(
            success=True,
            message="Heatwave simulation initiated - warning call sent",
            call_initiated=True,
            call_id=call_result.get("call_id")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate heatwave: {str(e)}")

@app.post("/simulation/complete")
async def simulation_complete():
    """
    Called when simulation is complete to send resolution call
    """
    try:
        if not voice_service:
            raise HTTPException(status_code=500, detail="Voice service not available")

        # Get homeowner phone number
        phone_numbers = [homeowner.phone_number for homeowner in registered_homeowners.values()]
        if not phone_numbers:
            raise HTTPException(status_code=400, detail="No homeowners registered")

        # Send resolution call
        resolution_result = await voice_service.send_resolution_call(phone_numbers[0], home_status)
        
        return AlertResponse(
            success=True,
            message="Resolution call sent successfully",
            call_initiated=True,
            call_id=resolution_result.get("call_id")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send resolution call: {str(e)}")

@app.post("/simulation/reset")
async def reset_simulation():
    """
    Reset home status to initial state and clear all registered homeowners
    """
    global home_status, registered_homeowners
    home_status = HomeStatus(
        battery_level=45.0,
        thermostat_temp=72.0,
        market_status="monitoring",
        energy_sold=0.0,
        profit_generated=0.0,
        solar_charging=False,
        ac_running=False,
        last_updated=datetime.utcnow()
    )
    
    # Clear all registered homeowners
    registered_homeowners.clear()
    
    return {"success": True, "message": "Simulation reset successfully - all data cleared"}
