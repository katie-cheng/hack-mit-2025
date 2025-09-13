from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum

class HomeownerRegistration(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=20)

class RegisteredHomeowner(BaseModel):
    id: str
    name: str
    phone_number: str
    registered_at: datetime

class RegistrationResponse(BaseModel):
    success: bool
    message: str
    homeowner_id: str

class SmartHomeDevice(BaseModel):
    device_id: str
    device_type: Literal["battery", "thermostat", "market", "solar"]
    name: str
    status: str
    value: float
    unit: str
    last_updated: datetime

class HomeStatus(BaseModel):
    battery_level: float = Field(..., ge=0, le=100)  # Percentage
    thermostat_temp: float = Field(..., ge=60, le=80)  # Fahrenheit
    market_status: Literal["monitoring", "executing_sale", "success", "idle"]
    energy_sold: float = Field(default=0)  # kWh
    profit_generated: float = Field(default=0)  # USD
    solar_charging: bool = Field(default=False)
    ac_running: bool = Field(default=False)
    last_updated: datetime

class WeatherEvent(BaseModel):
    event_type: Literal["heatwave", "storm", "cold_snap", "normal"]
    probability: float = Field(..., ge=0, le=100)  # Percentage
    severity: Literal["low", "medium", "high", "extreme"]
    predicted_time: str
    description: str

class SmartHomeAlert(BaseModel):
    alert_type: Literal["warning", "resolution"]
    weather_event: WeatherEvent
    message: str
    action_required: bool = False
    homeowner_consent: bool = False

class AlertResponse(BaseModel):
    success: bool
    message: str
    call_initiated: bool
    call_id: Optional[str] = None

class HomeStatusResponse(BaseModel):
    success: bool
    status: HomeStatus
    message: str

class SimulationRequest(BaseModel):
    simulation_type: Literal["heatwave", "storm", "normal"]
    duration_minutes: int = Field(default=5, ge=1, le=60)