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
# FastAPI routers for AURA APIs
from .home_state_api import router as home_state_router
from .threat_assessment_api import router as threat_assessment_router
from .integration_api import router as integration_router

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

# Call tracking to prevent infinite loops
warning_call_ids: set = set()  # Track warning call IDs that should trigger follow-ups
resolution_call_ids: set = set()  # Track resolution call IDs that should NOT trigger follow-ups

# Initialize services
voice_service: Optional[AURAVoiceService] = None
simulator: Optional[SmartHomeSimulator] = None
agent_orchestrator = None


@app.on_event("startup")
async def startup_event():
    global voice_service, simulator, agent_orchestrator
    try:
        voice_service = AURAVoiceService()
        simulator = SmartHomeSimulator(home_status_ref=home_status)
        
        # Initialize agent orchestrator
        from .agent_orchestrator import orchestrator
        agent_orchestrator = orchestrator
        await agent_orchestrator.initialize()
        
        print("✅ AURA services initialized successfully")
        print("✅ AURA Agent Orchestrator initialized with 4-agent system")
    except ValueError as e:
        print(f"❌ Service initialization failed: {e}")
    except Exception as e:
        print(f"❌ Agent orchestrator initialization failed: {e}")
        # Continue without agents if they fail to initialize


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
        
        # Track this as a warning call that should trigger follow-up
        if call_result.get("call_id"):
            warning_call_ids.add(call_result.get("call_id"))
            print(f"📝 Tracked warning call ID: {call_result.get('call_id')}")
        
        # Start background simulation (this will now be triggered by webhook)
        background_tasks.add_task(simulator.simulate_heatwave_response)
        
        return AlertResponse(
            success=True,
            message="Heatwave simulation initiated - warning call sent. Resolution call will be triggered after first call ends.",
            call_initiated=True,
            call_id=call_result.get("call_id")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate heatwave: {str(e)}")

@app.post("/simulation/complete")
async def simulation_complete():
    """
    Called when simulation is complete - resolution call will be handled by webhook
    """
    try:
        print("📞 Simulation completed - resolution call will be triggered by webhook when first call ends")
        
        return AlertResponse(
            success=True,
            message="Simulation completed - resolution call will be triggered by webhook",
            call_initiated=False,
            call_id=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete simulation: {str(e)}")

@app.post("/vapi-webhook")
async def vapi_webhook(request: dict, background_tasks: BackgroundTasks):
    """
    Handle Vapi webhook events for call lifecycle management
    """
    try:
        message = request.get("message", {})
        message_type = message.get("type")
        
        print(f"📞 Vapi webhook received: {message_type}")
        
        # Only proceed when the first call has ended
        is_call_ended = (
            (message_type == "status-update" and message.get("status") == "ended") or
            message_type == "end-of-call-report"
        )
        
        if not is_call_ended:
            print(f"   ⏳ Call still active, waiting...")
            return {"status": "acknowledged"}
        
        # Get call details
        call_info = message.get("call", {})
        call_id = call_info.get("id")
        customer_number = call_info.get("customer", {}).get("number")
        ended_reason = message.get("endedReason")
        
        print(f"   📞 Call ended: {call_id}")
        print(f"   📱 Customer: {customer_number}")
        print(f"   🔚 Reason: {ended_reason}")
        
        # Skip if it's voicemail, no answer, or assistant ended call
        if ended_reason in ["voicemail", "customer-did-not-answer", "assistant-ended-call"]:
            print(f"   ⏭️ Skipping follow-up due to reason: {ended_reason}")
            return {"status": "skipped"}
        
        # CRITICAL: Only process warning calls, not resolution calls
        if call_id not in warning_call_ids:
            print(f"   ⏭️ Skipping follow-up - call {call_id} is not a tracked warning call")
            return {"status": "not_warning_call"}
        
        # Remove from warning calls since we're processing it
        warning_call_ids.discard(call_id)
        
        # Check if this is a warning call that needs a follow-up
        if call_id and customer_number:
            # Store the call info for the follow-up
            global pending_follow_ups
            if 'pending_follow_ups' not in globals():
                pending_follow_ups = {}
            
            # Check if this call is already being processed
            if call_id in pending_follow_ups:
                print(f"   ⚠️ Call {call_id} already queued for follow-up, skipping")
                return {"status": "already_queued"}
            
            pending_follow_ups[call_id] = {
                "customer_number": customer_number,
                "ended_at": datetime.utcnow(),
                "processed": False
            }
            
            print(f"   ✅ Queued follow-up call for {customer_number}")
            
            # Start the follow-up process in background
            background_tasks.add_task(process_follow_up_call, call_id, customer_number)
        
        return {"status": "processed"}
        
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

async def process_follow_up_call(call_id: str, customer_number: str):
    """
    Process the follow-up call after delay
    """
    try:
        print(f"🔄 Processing follow-up for call {call_id}")
        
        # Wait 15 seconds before making the follow-up call
        print("⏳ Waiting 15 seconds before follow-up call...")
        await asyncio.sleep(15)
        
        # Check if we still have the call info
        global pending_follow_ups
        if 'pending_follow_ups' not in globals() or call_id not in pending_follow_ups:
            print(f"   ⚠️ Call {call_id} no longer in pending list")
            return
        
        call_info = pending_follow_ups[call_id]
        if call_info.get("processed", False):
            print(f"   ⚠️ Call {call_id} already processed")
            return
        
        # Mark as processed
        pending_follow_ups[call_id]["processed"] = True
        
        # Make the resolution call
        if voice_service:
            print(f"📞 Making resolution call to {customer_number}")
            resolution_result = await voice_service.send_resolution_call(customer_number, home_status)
            
            if resolution_result.get("success"):
                resolution_call_id = resolution_result.get('call_id')
                print(f"   ✅ Resolution call successful: {resolution_call_id}")
                
                # Track this as a resolution call that should NOT trigger follow-up
                if resolution_call_id:
                    resolution_call_ids.add(resolution_call_id)
                    print(f"📝 Tracked resolution call ID: {resolution_call_id}")
            else:
                print(f"   ❌ Resolution call failed: {resolution_result.get('message')}")
        else:
            print("   ❌ Voice service not available")
        
        # Clean up
        del pending_follow_ups[call_id]
        
    except Exception as e:
        print(f"❌ Follow-up call error: {str(e)}")

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

# Include AURA API routers
app.include_router(home_state_router)
app.include_router(threat_assessment_router)
app.include_router(integration_router)
