from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Any
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    """Types of actions that can be performed on home devices"""
    READ = "read"
    SET = "set"
    TOGGLE = "toggle"
    ADJUST = "adjust"

class DeviceType(str, Enum):
    """Types of devices in the smart home"""
    THERMOSTAT = "thermostat"
    BATTERY = "battery"
    SOLAR = "solar"
    GRID = "grid"

class Action(BaseModel):
    """Individual action to perform on a device"""
    device_type: DeviceType
    action_type: ActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    target_value: Optional[float] = None
    
    class Config:
        json_encoders = {
            DeviceType: lambda v: v.value,
            ActionType: lambda v: v.value
        }


class HomeStateRequest(BaseModel):
    """Request model for Home State Agent operations"""
    actions: List[Action] = Field(description="List of actions to execute")
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DeviceState(BaseModel):
    """State of an individual device"""
    device_type: DeviceType
    status: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class HomeMetadata(BaseModel):
    """Metadata about the home"""
    home_id: str
    location: str
    owner_name: Optional[str] = None
    timezone: str = "UTC"


class FinancialData(BaseModel):
    """Financial information related to energy management"""
    profit_today_usd: float = 0.0
    energy_cost_savings_usd: float = 0.0
    total_energy_sold_kwh: float = 0.0
    total_energy_purchased_kwh: float = 0.0


class HomeState(BaseModel):
    """Complete state of the smart home"""
    metadata: HomeMetadata
    devices: Dict[str, DeviceState] = Field(default_factory=dict)
    financials: FinancialData = Field(default_factory=FinancialData)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    def get_device(self, device_type: DeviceType) -> Optional[DeviceState]:
        """Get device state by type"""
        return self.devices.get(device_type.value)
    
    def update_device(self, device_type: DeviceType, properties: Dict[str, Any]):
        """Update device properties"""
        device_key = device_type.value
        if device_key in self.devices:
            self.devices[device_key].properties.update(properties)
            self.devices[device_key].last_updated = datetime.utcnow()
        else:
            self.devices[device_key] = DeviceState(
                device_type=device_type,
                status="active",
                properties=properties
            )
        self.last_updated = datetime.utcnow()


class ActionResult(BaseModel):
    """Result of executing an action"""
    action: Action
    success: bool
    message: str
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HomeStateResult(BaseModel):
    """Response from Home State Agent operations"""
    success: bool
    message: str
    home_state: HomeState
    action_results: List[ActionResult] = Field(default_factory=list)
    request_id: Optional[str] = None
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HomeAssistantEntity(BaseModel):
    """Home Assistant entity representation"""
    entity_id: str
    state: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    last_changed: datetime = Field(default_factory=datetime.utcnow)


class TeslaFleetStatus(BaseModel):
    """Tesla Fleet API status representation"""
    vehicle_id: Optional[str] = None
    battery_level: float = 0.0
    charging_state: str = "Disconnected"
    charge_limit_soc: int = 80
    powerwall_id: Optional[str] = None
    powerwall_soc: float = 0.0
    grid_status: str = "SystemGridConnected"
