from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Any
from datetime import datetime
from enum import Enum


class ThreatLevel(str, Enum):
    """Threat level classifications"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str, Enum):
    """Types of threats that can be assessed"""
    HEAT_WAVE = "heat_wave"
    GRID_STRAIN = "grid_strain"
    POWER_OUTAGE = "power_outage"
    ENERGY_SHORTAGE = "energy_shortage"
    COMBINED = "combined"


class WeatherData(BaseModel):
    """Weather data from OpenWeatherMap API"""
    location: str
    temperature_f: float
    condition: str
    humidity_percent: Optional[float] = None
    wind_speed_mph: Optional[float] = None
    nws_alert: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "openweathermap"


class GridData(BaseModel):
    """Grid data from EIA API"""
    balancing_authority: str
    timestamp_utc: datetime
    frequency_hz: float
    current_demand_mw: float
    status: str
    reserve_margin_mw: Optional[float] = None
    source: str = "eia"


class ThreatIndicator(BaseModel):
    """Individual threat indicator"""
    indicator_type: str
    value: float
    threshold: float
    severity: ThreatLevel
    description: str
    confidence: float = Field(ge=0.0, le=1.0)


class ThreatAnalysis(BaseModel):
    """Synthesized threat analysis"""
    overall_threat_level: ThreatLevel
    threat_types: List[ThreatType]
    primary_concerns: List[str]
    recommended_actions: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    analysis_summary: str
    indicators: List[ThreatIndicator] = Field(default_factory=list)


class ThreatAnalysisRequest(BaseModel):
    """Request model for Threat Assessment Agent"""
    location: str = Field(description="Location to analyze (e.g., 'Austin, TX')")
    include_weather: bool = Field(default=True, description="Include weather data analysis")
    include_grid: bool = Field(default=True, description="Include grid data analysis")
    include_research: bool = Field(default=False, description="Include Perplexity research")
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ThreatAnalysisResult(BaseModel):
    """Response from Threat Assessment Agent"""
    success: bool
    message: str
    analysis: Optional[ThreatAnalysis] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIError(BaseModel):
    """API error information"""
    api_name: str
    error_message: str
    status_code: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DataSourceStatus(BaseModel):
    """Status of data sources"""
    weather_api: bool = True
    grid_api: bool = True
    research_api: bool = True
    errors: List[APIError] = Field(default_factory=list)


class OpenWeatherMapResponse(BaseModel):
    """OpenWeatherMap API response structure"""
    main: Dict[str, Any]
    weather: List[Dict[str, Any]]
    wind: Optional[Dict[str, Any]] = None
    name: str
    sys: Optional[Dict[str, Any]] = None


class EIAResponse(BaseModel):
    """EIA API response structure"""
    series: List[Dict[str, Any]]
    request: Dict[str, Any]


class PerplexityResponse(BaseModel):
    """Perplexity API response structure"""
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, Any]] = None


class MockDataConfig(BaseModel):
    """Configuration for using mock data"""
    use_mock_weather: bool = False
    use_mock_grid: bool = False
    mock_weather_file: str = "mock_weather_data.json"
    mock_grid_file: str = "mock_grid_data.json"
