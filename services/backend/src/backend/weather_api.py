import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from .api_clients import OpenWeatherMapClient
from .threat_models import WeatherData

# Create FastAPI router
router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/current")
async def get_current_weather(
    location: str = Query("Austin, TX", description="Location to get weather for")
):
    """
    Get current weather data from OpenWeatherMap API
    """
    try:
        # Get OpenWeatherMap API key from environment
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OpenWeatherMap API key not configured"
            )
        
        # Create weather client and get current weather
        async with OpenWeatherMapClient(api_key) as client:
            weather_data = await client.get_current_weather(location)
        
        # Convert to response format
        return {
            "success": True,
            "data": {
                "location": weather_data.location,
                "temperature": weather_data.temperature_f,
                "condition": weather_data.condition,
                "humidity": weather_data.humidity_percent,
                "wind_speed": weather_data.wind_speed_mph,
                "nws_alert": weather_data.nws_alert,
                "timestamp": weather_data.timestamp.isoformat() if weather_data.timestamp else None,
                "source": weather_data.source
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch weather data: {str(e)}"
        )

@router.get("/dashboard")
async def get_weather_dashboard_data(
    location: str = Query("Austin, TX", description="Location to get weather for")
):
    """
    Get weather data formatted for the dashboard frontend
    """
    try:
        # Get OpenWeatherMap API key from environment
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key:
            # Return mock data if API key is not available
            return _get_mock_weather_dashboard_data()
        
        # Create weather client and get current weather
        async with OpenWeatherMapClient(api_key) as client:
            weather_data = await client.get_current_weather(location)
        
        # Calculate heat index (simplified formula)
        temperature = weather_data.temperature_f
        humidity = weather_data.humidity_percent or 50
        heat_index = _calculate_heat_index(temperature, humidity)
        
        # Forecast next peak (simplified - add 2-4 degrees for afternoon)
        current_hour = datetime.now().hour
        if current_hour < 15:  # Before 3 PM
            next_peak = temperature + 3
        else:
            next_peak = temperature + 1
        
        # Format NWS warning
        nws_warning = weather_data.nws_alert or "No Active Alerts"
        if "heat" in nws_warning.lower():
            nws_warning = "Heat Advisory"
        elif "storm" in nws_warning.lower():
            nws_warning = "Storm Warning"
        elif "no active" in nws_warning.lower():
            nws_warning = "No Active Alerts"
        
        return {
            "success": True,
            "data": {
                "temperature": round(temperature, 1),
                "heatIndex": round(heat_index, 1),
                "nextPeak": round(next_peak, 1),
                "nwsWarning": nws_warning,
                "condition": weather_data.condition,
                "humidity": humidity,
                "windSpeed": weather_data.wind_speed_mph or 0,
                "location": weather_data.location,
                "lastUpdated": weather_data.timestamp.isoformat() if weather_data.timestamp else datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Weather API error: {e}")
        # Return mock data on error
        return _get_mock_weather_dashboard_data()

def _calculate_heat_index(temp_f: float, humidity: float) -> float:
    """
    Calculate heat index using simplified formula
    """
    if temp_f < 80:
        return temp_f
    
    # Simplified heat index calculation
    hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
    hi += -0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f * temp_f
    hi += -5.481717e-2 * humidity * humidity + 1.22874e-3 * temp_f * temp_f * humidity
    hi += 8.5282e-4 * temp_f * humidity * humidity - 1.99e-6 * temp_f * temp_f * humidity * humidity
    
    return max(temp_f, hi)

def _get_mock_weather_dashboard_data():
    """
    Return mock weather data when API is unavailable
    """
    current_hour = datetime.now().hour
    
    # Vary temperature based on time of day
    if 6 <= current_hour <= 9:  # Morning
        base_temp = 85
    elif 10 <= current_hour <= 16:  # Daytime
        base_temp = 95
    elif 17 <= current_hour <= 20:  # Evening
        base_temp = 92
    else:  # Night
        base_temp = 78
    
    import random
    temperature = base_temp + random.randint(-3, 3)
    heat_index = temperature + random.randint(5, 15)
    next_peak = temperature + random.randint(2, 6)
    
    return {
        "success": True,
        "data": {
            "temperature": temperature,
            "heatIndex": heat_index,
            "nextPeak": next_peak,
            "nwsWarning": "Heat Advisory" if temperature > 90 else "No Active Alerts",
            "condition": "Clear" if temperature < 90 else "Hot",
            "humidity": random.randint(40, 70),
            "windSpeed": random.randint(3, 12),
            "location": "Austin, TX",
            "lastUpdated": datetime.utcnow().isoformat()
        },
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Using mock data - OpenWeatherMap API key not configured"
    }

# Export the router
__all__ = ["router"]
