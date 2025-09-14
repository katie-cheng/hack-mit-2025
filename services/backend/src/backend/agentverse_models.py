"""
Data models for AURA Smart Home Management Agent
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HomeStatus(BaseModel):
    """Current status of the smart home"""
    battery_level: float = Field(default=45.0, description="Battery charge level (0-100%)")
    thermostat_temp: float = Field(default=72.0, description="Current thermostat temperature (°F)")
    market_status: str = Field(default="monitoring", description="Energy market status")
    energy_sold: float = Field(default=0.0, description="Energy sold (kWh)")
    profit_generated: float = Field(default=0.0, description="Profit generated ($)")
    solar_charging: bool = Field(default=False, description="Solar charging status")
    ac_running: bool = Field(default=False, description="AC running status")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class Homeowner(BaseModel):
    """Registered homeowner information"""
    name: str = Field(description="Homeowner name")
    phone_number: str = Field(description="Phone number in E.164 format")
    registered_at: datetime = Field(default_factory=datetime.utcnow, description="Registration timestamp")


class WeatherEvent(BaseModel):
    """Weather event information"""
    event_type: str = Field(description="Type of weather event (e.g., 'heatwave')")
    probability: float = Field(description="Probability of event (0-1)")
    severity: str = Field(description="Event severity (low, medium, high)")
    expected_time: str = Field(description="Expected time of event")
    description: str = Field(description="Event description")


class VoiceCallRequest(BaseModel):
    """Request to initiate a voice call"""
    phone_number: str = Field(description="Phone number to call")
    call_type: str = Field(description="Type of call (warning, resolution)")
    message: str = Field(description="Message to deliver")


class VoiceCallResponse(BaseModel):
    """Response from voice call initiation"""
    success: bool = Field(description="Whether call was initiated successfully")
    call_id: Optional[str] = Field(default=None, description="VAPI call ID if successful")
    message: str = Field(description="Response message")


class SimulationRequest(BaseModel):
    """Request to start a simulation"""
    event_type: str = Field(default="heatwave", description="Type of event to simulate")
    duration: int = Field(default=30, description="Simulation duration in seconds")


class SimulationResponse(BaseModel):
    """Response from simulation start"""
    success: bool = Field(description="Whether simulation started successfully")
    simulation_id: str = Field(description="Unique simulation ID")
    message: str = Field(description="Response message")


class AgentResponse(BaseModel):
    """Standard agent response format"""
    success: bool = Field(description="Whether operation was successful")
    message: str = Field(description="Response message")
    data: Optional[Dict] = Field(default=None, description="Additional response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
