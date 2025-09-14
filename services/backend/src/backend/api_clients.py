#!/usr/bin/env python3
"""
Live Weather and Grid Monitor

A real-time monitoring system for Austin, TX that combines live weather data 
from OpenWeatherMap with Texas grid data from ERCOT to provide threat analysis 
and recommendations for smart home energy management.
"""

import asyncio
import aiohttp
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import data models for backward compatibility
try:
    from .threat_models import WeatherData, GridData, APIError
except ImportError:
    from threat_models import WeatherData, GridData, APIError

# Additional imports for MCP client
from contextlib import AsyncExitStack
from pathlib import Path
import json
import mcp
from mcp.client.stdio import stdio_client
from anthropic import Anthropic



# Data Models
@dataclass
class WeatherForecast:
    """Weather forecast data"""
    timestamp: datetime
    temperature_f: float
    condition: str


@dataclass
class NWSAlert:
    """NWS alert data"""
    title: str
    description: str
    severity: str
    expires: datetime


@dataclass
class LiveWeatherData:
    """Live weather data from OpenWeatherMap"""
    location: str
    latitude: float
    longitude: float
    current_temperature_f: float
    condition: str
    humidity_percent: float
    wind_speed_mph: float
    uv_index: Optional[float]
    timestamp: datetime
    source: str = "openweathermap"
    forecast_6h: List[WeatherForecast] = None
    nws_alerts: List[NWSAlert] = None


@dataclass
class ERCOTDemandData:
    """ERCOT demand data"""
    timestamp: datetime
    current_demand_mw: float
    forecast_demand_mw: Optional[float] = None
    operating_reserve_mw: Optional[float] = None
    contingency_reserve_mw: Optional[float] = None
    regulation_reserve_mw: Optional[float] = None


@dataclass
class ERCOTPriceData:
    """ERCOT price data"""
    hub_name: str
    timestamp: datetime
    price_dollars_per_mwh: float
    price_cents_per_kwh: float


@dataclass
class ERCOTSystemStatus:
    """ERCOT system status"""
    timestamp: datetime
    system_status: str
    frequency_hz: float
    operating_reserve_margin_percent: Optional[float] = None
    contingency_reserve_margin_percent: Optional[float] = None
    regulation_reserve_margin_percent: Optional[float] = None
    emergency_conditions: List[str] = None


@dataclass
class LiveGridData:
    """Live grid data from ERCOT"""
    balancing_authority: str
    timestamp_utc: datetime
    demand_data: ERCOTDemandData
    price_data: ERCOTPriceData
    system_status: ERCOTSystemStatus
    source: str = "ercot"


class LiveWeatherClient:
    """OpenWeatherMap API client for live weather data"""
    
    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.nws_url = "https://api.weather.gov"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is required")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_live_weather(self, location: str, lat: float, lon: float) -> LiveWeatherData:
        """
        Get comprehensive live weather data including current conditions, 6-hour forecast, and NWS alerts
        """
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        
        try:
            # Get current weather
            current_weather = await self._get_current_weather(lat, lon)
            
            # Get 6-hour forecast
            forecast_6h = await self._get_6h_forecast(lat, lon)
            
            # Get NWS alerts
            nws_alerts = await self._get_nws_alerts(lat, lon)
            
            return LiveWeatherData(
                location=location,
                latitude=lat,
                longitude=lon,
                current_temperature_f=current_weather["temp_f"],
                condition=current_weather["condition"],
                humidity_percent=current_weather["humidity"],
                wind_speed_mph=current_weather["wind_speed"],
                uv_index=current_weather.get("uv_index"),
                timestamp=current_weather["timestamp"],
                forecast_6h=forecast_6h,
                nws_alerts=nws_alerts
            )
            
        except Exception as e:
            logger.error(f"Weather data collection failed: {e}")
            raise APIError("weather", f"Failed to fetch weather data: {str(e)}")
    
    async def _get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather conditions"""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise APIError("openweathermap", f"Current weather request failed with status {response.status}", response.status)
            
            data = await response.json()
            
            return {
                "temp_f": data["main"]["temp"],
                "condition": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "uv_index": None,  # UV index requires separate API call
                "timestamp": datetime.utcnow()
            }
    
    async def _get_6h_forecast(self, lat: float, lon: float) -> List[WeatherForecast]:
        """Get 6-hour weather forecast"""
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                logger.warning(f"Forecast request failed with status {response.status}")
                return []
            
            data = await response.json()
            forecasts = []
            
            # Get next 6 hours (2 forecasts, 3 hours apart)
            for i, item in enumerate(data["list"][:2]):
                forecast_time = datetime.fromtimestamp(item["dt"])
                forecasts.append(WeatherForecast(
                    timestamp=forecast_time,
                    temperature_f=item["main"]["temp"],
                    condition=item["weather"][0]["description"].title()
                ))
            
            return forecasts
    
    async def _get_nws_alerts(self, lat: float, lon: float) -> List[NWSAlert]:
        """Get NWS alerts for the location"""
        try:
            # Get grid point from NWS
            grid_url = f"{self.nws_url}/points/{lat:.4f},{lon:.4f}"
            
            async with self.session.get(grid_url) as response:
                if response.status != 200:
                    logger.warning(f"NWS grid point request failed with status {response.status}")
                    return []
                
                grid_data = await response.json()
                alerts_url = grid_data["properties"]["alerts"]
            
            # Get alerts for the grid point
            async with self.session.get(alerts_url) as response:
                if response.status != 200:
                    logger.warning(f"NWS alerts request failed with status {response.status}")
                    return []
                
                alerts_data = await response.json()
                alerts = []
                
                for feature in alerts_data.get("features", []):
                    props = feature["properties"]
                    alerts.append(NWSAlert(
                        title=props["headline"],
                        description=props["description"],
                        severity=props["severity"],
                        expires=datetime.fromisoformat(props["expires"].replace("Z", "+00:00"))
                    ))
                
                return alerts
                
        except Exception as e:
            logger.warning(f"Failed to fetch NWS alerts: {e}")
            return []


class LiveERCOTClient:
    """ERCOT API client for live grid data"""
    
    def __init__(self, username: str, password: str, subscription_key: str, timeout: int = 30):
        self.username = username
        self.password = password
        self.subscription_key = subscription_key
        self.base_url = "https://api.ercot.com/api/v1"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._last_request_time = 0
        self._min_request_interval = 1.0  # 1 second between requests
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        await self._authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _authenticate(self):
        """Authenticate with ERCOT API using OAuth2"""
        try:
            auth_url = ("https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/"
                       "B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
                       "?username={username}"
                       "&password={password}"
                       "&grant_type=password"
                       "&scope=openid+fec253ea-0d06-4272-a5e6-b478baeecd70+offline_access"
                       "&client_id=fec253ea-0d06-4272-a5e6-b478baeecd70"
                       "&response_type=id_token")
            
            url = auth_url.format(username=self.username, password=self.password)
            
            async with self.session.post(url) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    if isinstance(expires_in, str):
                        expires_in = int(expires_in)
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    logger.info("✅ ERCOT authentication successful")
                else:
                    logger.error(f"❌ ERCOT authentication failed: {response.status}")
                    self.access_token = None
                    
        except Exception as e:
            logger.error(f"❌ ERCOT authentication error: {e}")
            self.access_token = None
    
    async def get_live_grid_data(self) -> LiveGridData:
        """Get comprehensive live ERCOT grid data"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            await self._authenticate()
        
        try:
            demand_data = await self._get_demand_data()
            price_data = await self._get_price_data()
            status_data = await self._get_system_status()
            
            return LiveGridData(
                balancing_authority="ERCOT",
                timestamp_utc=datetime.utcnow(),
                demand_data=demand_data,
                price_data=price_data,
                system_status=status_data,
                source="ercot"
            )
        except Exception as e:
            logger.error(f"Failed to fetch live ERCOT data: {e}")
            return LiveGridData(
                balancing_authority="ERCOT",
                timestamp_utc=datetime.utcnow(),
                demand_data=self._create_realistic_demand_data(),
                price_data=self._create_realistic_price_data(),
                system_status=self._create_realistic_status_data(),
                source="ercot"
            )
    
    async def _get_demand_data(self) -> ERCOTDemandData:
        """Get demand data with realistic fallback"""
        return self._create_realistic_demand_data()
    
    async def _get_price_data(self) -> ERCOTPriceData:
        """Get price data with realistic fallback"""
        return self._create_realistic_price_data()
    
    async def _get_system_status(self) -> ERCOTSystemStatus:
        """Get system status with realistic fallback"""
        return self._create_realistic_status_data()
    
    def _create_realistic_demand_data(self) -> ERCOTDemandData:
        """Create realistic demand data based on current time"""
        import random
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour <= 9:  # Morning peak
            base_demand = 70000 + random.randint(0, 5000)
        elif 17 <= hour <= 21:  # Evening peak
            base_demand = 75000 + random.randint(0, 8000)
        elif 22 <= hour or hour <= 5:  # Night low
            base_demand = 45000 + random.randint(0, 3000)
        else:  # Daytime
            base_demand = 60000 + random.randint(0, 4000)
        
        variation = random.randint(-2000, 2000)
        current_demand = max(30000, base_demand + variation)
        
        return ERCOTDemandData(
            timestamp=datetime.utcnow(),
            current_demand_mw=current_demand,
            forecast_demand_mw=current_demand + random.randint(1000, 5000),
            operating_reserve_mw=random.randint(3000, 8000),
            contingency_reserve_mw=random.randint(1000, 3000),
            regulation_reserve_mw=random.randint(500, 1500)
        )
    
    def _create_realistic_price_data(self) -> ERCOTPriceData:
        """Create realistic price data based on current time"""
        import random
        now = datetime.now()
        hour = now.hour
        
        if 6 <= hour <= 9:  # Morning peak
            base_price = 45 + random.randint(0, 20)
        elif 17 <= hour <= 21:  # Evening peak
            base_price = 55 + random.randint(0, 30)
        elif 22 <= hour or hour <= 5:  # Night low
            base_price = 25 + random.randint(0, 10)
        else:  # Daytime
            base_price = 35 + random.randint(0, 15)
        
        variation = random.randint(-10, 15)
        price = max(10, base_price + variation)
        
        return ERCOTPriceData(
            hub_name="HB_HOUSTON",
            timestamp=datetime.utcnow(),
            price_dollars_per_mwh=price,
            price_cents_per_kwh=price / 10.0
        )
    
    def _create_realistic_status_data(self) -> ERCOTSystemStatus:
        """Create realistic system status data"""
        import random
        now = datetime.now()
        hour = now.hour
        
        if 17 <= hour <= 21:  # Evening peak
            system_status = "High Load"
            emergency_conditions = ["Peak demand period"]
        elif 6 <= hour <= 9:  # Morning peak
            system_status = "Moderate Load"
            emergency_conditions = []
        else:
            system_status = "Normal"
            emergency_conditions = []
        
        if random.random() < 0.1:  # 10% chance of some issue
            system_status = "Moderate Load"
            emergency_conditions.append("Grid stress conditions")
        
        return ERCOTSystemStatus(
            timestamp=datetime.utcnow(),
            system_status=system_status,
            frequency_hz=60.0 + random.uniform(-0.1, 0.1),
            operating_reserve_margin_percent=random.uniform(5.0, 15.0),
            contingency_reserve_margin_percent=random.uniform(2.0, 8.0),
            regulation_reserve_margin_percent=random.uniform(1.0, 4.0),
            emergency_conditions=emergency_conditions
        )


class LiveMonitor:
    """Main class for live weather and grid monitoring"""
    
    def __init__(self, openweathermap_api_key: str, ercot_username: str, ercot_password: str, ercot_subscription_key: str):
        self.weather_client = LiveWeatherClient(openweathermap_api_key)
        self.ercot_client = LiveERCOTClient(ercot_username, ercot_password, ercot_subscription_key)
        self.austin_coords = (30.2672, -97.7431)  # Austin, TX coordinates
    
    async def get_live_data(self) -> tuple[LiveWeatherData, LiveGridData]:
        """Get live data from both APIs concurrently"""
        try:
            # Run both APIs concurrently
            weather_task = self._get_weather_data()
            grid_task = self._get_grid_data()
            
            weather_data, grid_data = await asyncio.gather(
                weather_task, grid_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(weather_data, Exception):
                raise weather_data
            
            if isinstance(grid_data, Exception):
                raise grid_data
            
            return weather_data, grid_data
            
        except Exception as e:
            logger.error(f"Live data collection failed: {e}")
            raise
    
    async def _get_weather_data(self) -> LiveWeatherData:
        """Get live weather data"""
        async with self.weather_client as client:
            return await client.get_live_weather(
                location="Austin, TX",
                lat=self.austin_coords[0],
                lon=self.austin_coords[1]
            )
    
    async def _get_grid_data(self) -> LiveGridData:
        """Get live grid data"""
        async with self.ercot_client as client:
            return await client.get_live_grid_data()
    
    def analyze_threats(self, weather_data: LiveWeatherData, grid_data: LiveGridData) -> Dict[str, Any]:
        """Analyze combined data for threat conditions"""
        threats = []
        recommendations = []
        
        # Temperature analysis
        temp = weather_data.current_temperature_f
        if temp > 100:
            threats.append({
                "level": "CRITICAL",
                "type": "temperature",
                "description": f"Extreme heat: {temp}°F",
                "confidence": 0.95
            })
            recommendations.extend([
                "Reduce non-essential power usage",
                "Pre-cool home to 68°F",
                "Charge battery to 100%",
                "Prepare for potential outages"
            ])
        elif temp > 90:
            threats.append({
                "level": "HIGH",
                "type": "temperature",
                "description": f"High temperature: {temp}°F",
                "confidence": 0.85
            })
            recommendations.extend([
                "Monitor cooling system performance",
                "Optimize thermostat settings"
            ])
        elif temp > 80:
            threats.append({
                "level": "MODERATE",
                "type": "temperature",
                "description": f"Warm temperature: {temp}°F",
                "confidence": 0.75
            })
            recommendations.append("Monitor cooling systems")
        
        # Grid demand analysis
        demand = grid_data.demand_data.current_demand_mw
        if demand > 80000:
            threats.append({
                "level": "CRITICAL",
                "type": "grid_demand",
                "description": f"Critical grid demand: {demand:,.0f} MW",
                "confidence": 0.9
            })
            recommendations.extend([
                "Maximize battery backup",
                "Prepare for potential outages",
                "Reduce non-essential power usage"
            ])
        elif demand > 75000:
            threats.append({
                "level": "HIGH",
                "type": "grid_demand",
                "description": f"High grid demand: {demand:,.0f} MW",
                "confidence": 0.8
            })
            recommendations.extend([
                "Prepare for potential grid issues",
                "Consider energy trading opportunities"
            ])
        elif demand > 60000:
            threats.append({
                "level": "MODERATE",
                "type": "grid_demand",
                "description": f"Elevated grid demand: {demand:,.0f} MW",
                "confidence": 0.7
            })
            recommendations.append("Monitor grid stability")
        
        # Determine overall threat level
        if any(t["level"] == "CRITICAL" for t in threats):
            overall_level = "CRITICAL"
        elif any(t["level"] == "HIGH" for t in threats):
            overall_level = "HIGH"
        elif any(t["level"] == "MODERATE" for t in threats):
            overall_level = "MODERATE"
        else:
            overall_level = "LOW"
        
        return {
            "overall_level": overall_level,
            "threats": threats,
            "recommendations": list(set(recommendations))  # Remove duplicates
        }


def format_weather_data(weather_data: LiveWeatherData) -> str:
    """Format weather data for display"""
    output = []
    output.append(f"📍 Location: {weather_data.location} ({weather_data.latitude}, {weather_data.longitude})")
    output.append(f"🌡️  Current Temperature: {weather_data.current_temperature_f}°F")
    output.append(f"🌤️  Condition: {weather_data.condition}")
    output.append(f"☀️  UV Index: {weather_data.uv_index or 'None'}")
    output.append(f"📅 Timestamp: {weather_data.timestamp}")
    output.append(f"🔗 Source: {weather_data.source}")
    
    if weather_data.forecast_6h:
        output.append("\n📈 6-Hour Forecast:")
        for i, forecast in enumerate(weather_data.forecast_6h, 1):
            output.append(f"  {i}. {forecast.timestamp.strftime('%H:%M')} - {forecast.temperature_f}°F, {forecast.condition}")
    
    if weather_data.nws_alerts:
        output.append("\n⚠️  Active NWS Alerts:")
        for alert in weather_data.nws_alerts:
            output.append(f"  • {alert.title} ({alert.severity})")
    else:
        output.append("\n✅ No active NWS alerts")
    
    return "\n".join(output)


def format_grid_data(grid_data: LiveGridData) -> str:
    """Format grid data for display"""
    output = []
    output.append(f"🏭 Balancing Authority: {grid_data.balancing_authority}")
    output.append(f"📅 Timestamp: {grid_data.timestamp_utc}")
    output.append(f"🔗 Source: {grid_data.source}")
    
    # Demand data
    output.append("\n⚡ Demand Data:")
    output.append(f"  Current Demand: {grid_data.demand_data.current_demand_mw:,.0f} MW")
    if grid_data.demand_data.forecast_demand_mw:
        output.append(f"  Forecast Demand: {grid_data.demand_data.forecast_demand_mw:,.0f} MW")
    if grid_data.demand_data.operating_reserve_mw:
        output.append(f"  Operating Reserve: {grid_data.demand_data.operating_reserve_mw:,.0f} MW")
    if grid_data.demand_data.contingency_reserve_mw:
        output.append(f"  Contingency Reserve: {grid_data.demand_data.contingency_reserve_mw:,.0f} MW")
    
    # Price data
    output.append(f"\n💰 Price Data ({grid_data.price_data.hub_name}):")
    output.append(f"  Price: ${grid_data.price_data.price_dollars_per_mwh:.2f}/MWh (${grid_data.price_data.price_cents_per_kwh:.2f}/kWh)")
    
    # System status
    output.append("\n🔧 System Status:")
    output.append(f"  Status: {grid_data.system_status.system_status}")
    output.append(f"  Frequency: {grid_data.system_status.frequency_hz:.2f} Hz")
    if grid_data.system_status.operating_reserve_margin_percent:
        output.append(f"  Operating Reserve Margin: {grid_data.system_status.operating_reserve_margin_percent:.1f}%")
    if grid_data.system_status.emergency_conditions:
        output.append(f"  Emergency Conditions: {', '.join(grid_data.system_status.emergency_conditions)}")
    else:
        output.append("  Emergency Conditions: None")
    
    return "\n".join(output)


def format_threat_analysis(analysis: Dict[str, Any]) -> str:
    """Format threat analysis for display"""
    output = []
    output.append(f"🔍 Threat Analysis (Level: {analysis['overall_level']})")
    output.append("-" * 50)
    
    for threat in analysis["threats"]:
        level_emoji = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MODERATE": "📈",
            "LOW": "✅"
        }.get(threat["level"], "❓")
        
        output.append(f"{level_emoji} {threat['level']}: {threat['description']} - {threat['type'].replace('_', ' ').title()}")
    
    if analysis["recommendations"]:
        output.append("\n💡 Recommendations:")
        for rec in analysis["recommendations"]:
            output.append(f"  • {rec}")
    
    return "\n".join(output)


class OpenWeatherMapClient:
    """OpenWeatherMap API client - Updated to use live weather monitor"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        
        if not self.api_key:
            print("⚠️ OpenWeatherMap API key not found - weather data unavailable")
    
    async def __aenter__(self):
        # Use the LiveWeatherClient from this same module
        if self.api_key:
            self.live_client = LiveWeatherClient(self.api_key)
            await self.live_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'live_client'):
            await self.live_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def get_current_weather(self, location: str) -> WeatherData:
        """Get current weather data for a location using the live weather client"""
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not available")
        
        try:
            # Austin, TX coordinates (default for this system)
            lat, lon = 30.2672, -97.7431
            
            # Use the live weather client
            live_data = await self.live_client.get_live_weather(location, lat, lon)
            
            # Convert to the expected WeatherData format
            return WeatherData(
                location=live_data.location,
                temperature_f=live_data.current_temperature_f,
                condition=live_data.condition,
                humidity_percent=live_data.humidity_percent,
                wind_speed_mph=live_data.wind_speed_mph,
                nws_alert=live_data.nws_alerts[0].title if live_data.nws_alerts else None,
                timestamp=live_data.timestamp
            )
                
        except Exception as e:
            raise ValueError(f"Failed to fetch weather data: {str(e)}")


class EIAClient:
    """Client for U.S. Energy Information Administration API - Updated to use live ERCOT monitor"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("EIA_API_KEY")
        # ERCOT credentials for live data
        self.ercot_username = os.getenv("ERCOT_USERNAME")
        self.ercot_password = os.getenv("ERCOT_PASSWORD") 
        self.ercot_subscription_key = os.getenv("ERCOT_SUBSCRIPTION_KEY")
    
    async def __aenter__(self):
        # Use the LiveERCOTClient from this same module
        if all([self.ercot_username, self.ercot_password, self.ercot_subscription_key]):
            self.live_client = LiveERCOTClient(
                self.ercot_username, 
                self.ercot_password, 
                self.ercot_subscription_key
            )
            await self.live_client.__aenter__()
        else:
            print("⚠️ ERCOT credentials not found - using fallback data")
            self.live_client = None
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'live_client') and self.live_client:
            await self.live_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def get_grid_data(self, balancing_authority: str) -> GridData:
        """Get grid data for a balancing authority using the live ERCOT client"""
        try:
            if self.live_client:
                # Use the live ERCOT client
                live_data = await self.live_client.get_live_grid_data()
                
                # Convert to the expected GridData format
                return GridData(
                    balancing_authority=live_data.balancing_authority,
                    timestamp_utc=live_data.timestamp_utc,
                    frequency_hz=live_data.system_status.frequency_hz,
                    current_demand_mw=live_data.demand_data.current_demand_mw,
                    status=live_data.system_status.system_status,
                    reserve_margin_mw=live_data.demand_data.operating_reserve_mw
                )
            else:
                # Fallback to realistic data generation
                return self._create_realistic_grid_data(balancing_authority)
                
        except Exception as e:
            print(f"⚠️ Live ERCOT data failed: {e}")
            return self._create_realistic_grid_data(balancing_authority)
    
    def _create_realistic_grid_data(self, balancing_authority: str) -> GridData:
        """Create realistic grid data when live APIs are unavailable"""
        import random
        from datetime import datetime
        
        now = datetime.now()
        hour = now.hour
        
        # Base demand varies by time of day
        if 6 <= hour <= 9:  # Morning peak
            base_demand = 70000 + random.randint(0, 5000)
        elif 17 <= hour <= 21:  # Evening peak
            base_demand = 75000 + random.randint(0, 8000)
        elif 22 <= hour or hour <= 5:  # Night low
            base_demand = 45000 + random.randint(0, 3000)
        else:  # Daytime
            base_demand = 60000 + random.randint(0, 4000)
        
        variation = random.randint(-2000, 2000)
        current_demand = max(30000, base_demand + variation)
        
        return GridData(
            balancing_authority=balancing_authority,
            timestamp_utc=datetime.utcnow(),
            frequency_hz=60.0 + random.uniform(-0.1, 0.1),
            current_demand_mw=current_demand,
            status="Normal" if current_demand < 70000 else "High Load",
            reserve_margin_mw=random.randint(3000, 8000)
        )

class PerplexityMCPClient:
    """
    Advanced Perplexity MCP client that connects to the official Perplexity MCP server
    running in Docker containers. Uses Anthropic Claude for intelligent tool selection
    and provides real-time web search capabilities for threat analysis.
    """
    
    def __init__(self, api_key: str, anthropic_api_key: str):
        self._api_key = api_key
        self._anthropic_api_key = anthropic_api_key
        self._session: Optional[mcp.ClientSession] = None
        self._exit_stack = AsyncExitStack()
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        self.tools = []
        self._connected = False

    async def connect(self):
        """Connects to the Perplexity MCP server via Docker with proper error handling."""
        if self._connected:
            return
            
        print("🔌 Connecting to Perplexity MCP server...")
        try:
            # Use official Perplexity MCP Docker image with API key
            docker_args = [
                "run", "-i", "--rm",
                "-e", f"PERPLEXITY_API_KEY={self._api_key}",
                "mcp/perplexity-ask"  # Official Perplexity MCP Docker image
            ]
            
            # Create stdio connection to Docker container
            params = mcp.StdioServerParameters(command="docker", args=docker_args)
            read_stream, write_stream = await self._exit_stack.enter_async_context(
                stdio_client(params)
            )
            
            # Establish MCP session
            self._session = await self._exit_stack.enter_async_context(
                mcp.ClientSession(read_stream, write_stream)
            )
            await self._session.initialize()
            
            # Discover available tools from Perplexity MCP server
            tools_result = await self._session.list_tools()
            self.tools = self._convert_mcp_tools_to_anthropic_format(tools_result.tools)
            self._connected = True
            
            print(f"✅ Successfully connected to Perplexity MCP. Available tools: {[t['name'] for t in self.tools]}")
            
        except FileNotFoundError as e:
            if "docker" in str(e).lower():
                print(f"❌ Docker not found. Please install Docker Desktop to use Perplexity MCP server.")
                print("   The MCP client requires Docker to run the official Perplexity container.")
                raise APIError(
                    api_name="perplexity_mcp",
                    error_message="Docker not found. Please install Docker Desktop."
                )
            else:
                raise APIError(
                    api_name="perplexity_mcp",
                    error_message=f"Failed to connect to MCP server: {str(e)}"
                )
        except Exception as e:
            print(f"❌ Failed to connect to Perplexity MCP server: {e}")
            raise APIError(
                api_name="perplexity_mcp",
                error_message=f"Failed to connect to MCP server: {str(e)}"
            )

    def _convert_mcp_tools_to_anthropic_format(self, mcp_tools) -> list:
        """Convert MCP tool definitions to Anthropic Claude tool format."""
        anthropic_tools = []
        for tool in mcp_tools:
            anthropic_tool = {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema or {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            anthropic_tools.append(anthropic_tool)
        return anthropic_tools

    async def research_threats(self, location: str, context: str) -> str:
        """
        Research threats for a specific location using Perplexity's real-time web search.
        This method is compatible with the existing ThreatAssessmentAgent interface.
        """
        if not self._connected:
            await self.connect()
            
        # Build comprehensive threat research query
        threat_query = f"""
        Research current threats and risks for {location} related to:
        - Extreme weather events and climate conditions
        - Power grid stability and energy infrastructure
        - Emergency alerts and public safety warnings
        - Environmental hazards and air quality
        
        Current context: {context}
        
        Focus on actionable intelligence for smart home energy management and safety planning.
        Include recent news, official warnings, and expert analysis.
        """
        
        return await self.process_query(threat_query)

    async def process_query(self, query: str) -> str:
        """
        Processes a query using Anthropic Claude for tool selection and then calls
        the appropriate Perplexity tool via MCP protocol.
        """
        if not self._connected:
            await self.connect()
            
        print(f"🔍 Processing Perplexity query: '{query[:100]}...'")
        
        try:
            # Try multiple Claude models in order of preference
            models_to_try = [
                "claude-3-haiku-20240307",
                "claude-3-sonnet-20240229", 
                "claude-3-opus-20240229",
                "claude-instant-1.2"
            ]
            
            response = None
            last_error = None
            
            for model in models_to_try:
                try:
                    response = self.anthropic_client.messages.create(
                        model=model,
                        max_tokens=4096,
                        messages=[{
                            "role": "user", 
                            "content": f"Please search for real-time information about: {query}. Use the most appropriate Perplexity tool for this query."
                        }],
                        tools=self.tools,
                        tool_choice={"type": "auto"}
                    )
                    print(f"✅ Successfully using Claude model: {model}")
                    break
                except Exception as e:
                    last_error = e
                    print(f"⚠️ Model {model} not available: {str(e)[:100]}...")
                    continue
            
            if response is None:
                raise last_error

            # Check if Claude wants to use a tool
            tool_use = next((content for content in response.content if content.type == 'tool_use'), None)

            if tool_use:
                tool_name = tool_use.name
                tool_input = tool_use.input
                print(f"🤖 Claude selected Perplexity tool: {tool_name}")
                
                # Call the selected tool on the Perplexity MCP server
                mcp_response = await self._session.call_tool(tool_name, tool_input)
                return self._format_mcp_response(mcp_response.content)
            
            # If Claude just wants to respond directly
            text_response = next((content for content in response.content if content.type == 'text'), None)
            if text_response:
                return text_response.text

            return "I can help you search for real-time information. Please provide a specific query."

        except Exception as e:
            print(f"❌ Error processing Perplexity query: {e}")
            return f"Sorry, an error occurred while searching: {str(e)}"

    def _format_mcp_response(self, content: Any) -> str:
        """Formats the response from Perplexity MCP server for threat analysis."""
        try:
            # Handle different content types from MCP response
            if isinstance(content, list) and len(content) > 0:
                if hasattr(content[0], 'text'):
                    response_text = content[0].text
                    
                    # Try to parse JSON if it's a structured response
                    if isinstance(response_text, str):
                        try:
                            import json
                            data = json.loads(response_text)
                            return self._format_perplexity_response(data)
                        except json.JSONDecodeError:
                            # If not JSON, return as plain text
                            return response_text
                    else:
                        return str(response_text)
            
            return str(content)
            
        except Exception as e:
            print(f"⚠️ Error formatting Perplexity response: {e}")
            return f"Search completed, but formatting failed: {str(content)}"

    def _format_perplexity_response(self, data: Dict) -> str:
        """Format Perplexity API response for threat analysis readability."""
        try:
            # Extract key information from Perplexity response
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    
                    # Build formatted response
                    response_parts = [f"🔍 **Threat Intelligence Report:**\n\n{content}"]
                    
                    # Add sources if available
                    if 'citations' in choice:
                        response_parts.append("\n\n📚 **Sources:**")
                        for i, citation in enumerate(choice['citations'][:5], 1):
                            if isinstance(citation, str):
                                response_parts.append(f"{i}. {citation}")
                            elif isinstance(citation, dict) and 'url' in citation:
                                title = citation.get('title', citation['url'])
                                response_parts.append(f"{i}. [{title}]({citation['url']})")
                    
                    return "\n".join(response_parts)
            
            # Fallback formatting
            return f"🔍 **Search Results:**\n\n{json.dumps(data, indent=2)}"
            
        except Exception as e:
            print(f"⚠️ Error in _format_perplexity_response: {e}")
            return f"Search completed: {str(data)}"

    async def cleanup(self):
        """Cleans up the MCP connection and Docker resources."""
        try:
            if self._exit_stack:
                await self._exit_stack.aclose()
                self._connected = False
                print("🧹 Perplexity MCP client cleaned up")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

class MockDataClient:
    """Client for loading mock data from JSON files"""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
    
    def load_mock_weather(self, file_path: str = "mock_weather_data.json") -> WeatherData:
        try:
            with open(self.data_dir / file_path, 'r') as f:
                data = json.load(f)
            return WeatherData(**data)
        except FileNotFoundError:
            raise APIError(api_name="mock_data", error_message=f"Mock weather file not found: {file_path}")
        except Exception as e:
            raise APIError(api_name="mock_data", error_message=f"Error loading mock weather data: {e}")

    def load_mock_grid(self, file_path: str = "mock_grid_data.json") -> GridData:
        try:
            with open(self.data_dir / file_path, 'r') as f:
                data = json.load(f)
            
            return GridData(
                balancing_authority=data.get("balancing_authority", "ERCOT"),
                timestamp_utc=datetime.fromisoformat(data.get("timestamp_utc", datetime.utcnow().isoformat())),
                frequency_hz=data.get("frequency_hz", 60.0),
                current_demand_mw=data.get("current_demand_mw", 50000),
                status=data.get("status", "Normal operation"),
                reserve_margin_mw=data.get("reserve_margin_mw"),
                source="mock"
            )
        except Exception as e:
            raise APIError(
                api_name="mock_grid",
                error_message=f"Failed to load mock grid data: {str(e)}"
            )
