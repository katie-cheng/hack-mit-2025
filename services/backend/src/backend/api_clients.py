import os
import json
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from .threat_models import (
    WeatherData, GridData, OpenWeatherMapResponse, EIAResponse, 
    PerplexityResponse, APIError, MockDataConfig
)


class OpenWeatherMapClient:
    """Client for OpenWeatherMap API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_current_weather(self, location: str) -> WeatherData:
        """Get current weather data for a location"""
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not provided")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Geocoding to get coordinates
            geo_url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "imperial"
            }
            
            async with self.session.get(geo_url, params=params) as response:
                if response.status != 200:
                    raise APIError(
                        api_name="openweathermap",
                        error_message=f"API request failed with status {response.status}",
                        status_code=response.status
                    )
                
                data = await response.json()
                return self._parse_weather_data(data, location)
                
        except Exception as e:
            raise APIError(
                api_name="openweathermap",
                error_message=f"Failed to fetch weather data: {str(e)}"
            )
    
    def _parse_weather_data(self, data: Dict[str, Any], location: str) -> WeatherData:
        """Parse OpenWeatherMap API response into WeatherData model"""
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        
        return WeatherData(
            location=location,
            temperature_f=main.get("temp", 0),
            condition=weather.get("main", "Unknown"),
            humidity_percent=main.get("humidity"),
            wind_speed_mph=wind.get("speed"),
            nws_alert=None,  # Would need separate NWS API call
            timestamp=datetime.utcnow(),
            source="openweathermap"
        )


class EIAClient:
    """Client for U.S. Energy Information Administration API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("EIA_API_KEY")
        self.base_url = "https://api.eia.gov/v2"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_grid_data(self, balancing_authority: str = "ERCOT") -> GridData:
        """Get current grid data for a balancing authority"""
        if not self.api_key:
            raise ValueError("EIA API key not provided")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Get real-time demand data
            url = f"{self.base_url}/electricity/rto/daily-regional-data"
            params = {
                "api_key": self.api_key,
                "frequency": "hourly",
                "data[0]": "value",
                "facets[respondent]": balancing_authority,
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise APIError(
                        api_name="eia",
                        error_message=f"API request failed with status {response.status}",
                        status_code=response.status
                    )
                
                data = await response.json()
                return self._parse_grid_data(data, balancing_authority)
                
        except Exception as e:
            raise APIError(
                api_name="eia",
                error_message=f"Failed to fetch grid data: {str(e)}"
            )
    
    def _parse_grid_data(self, data: Dict[str, Any], balancing_authority: str) -> GridData:
        """Parse EIA API response into GridData model"""
        series = data.get("response", {}).get("data", [])
        
        if not series:
            # Return default values if no data
            return GridData(
                balancing_authority=balancing_authority,
                timestamp_utc=datetime.utcnow(),
                frequency_hz=60.0,
                current_demand_mw=50000,
                status="Data unavailable",
                source="eia"
            )
        
        latest_data = series[0]
        
        return GridData(
            balancing_authority=balancing_authority,
            timestamp_utc=datetime.fromisoformat(latest_data.get("period", datetime.utcnow().isoformat())),
            frequency_hz=60.0,  # EIA doesn't provide frequency, using default
            current_demand_mw=latest_data.get("value", 50000),
            status="Normal operation",
            reserve_margin_mw=None,
            source="eia"
        )


class PerplexityClient:
    """Client for Perplexity AI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def research_threats(self, location: str, context: str) -> str:
        """Research current threats and conditions for a location"""
        if not self.api_key:
            raise ValueError("Perplexity API key not provided")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a threat assessment expert. Provide concise, factual information about current environmental and infrastructure threats."
                    },
                    {
                        "role": "user",
                        "content": f"Research current environmental and infrastructure threats for {location}. Context: {context}. Focus on heat waves, power grid issues, and energy shortages."
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            async with self.session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise APIError(
                        api_name="perplexity",
                        error_message=f"API request failed with status {response.status}",
                        status_code=response.status
                    )
                
                data = await response.json()
                return self._parse_research_response(data)
                
        except Exception as e:
            raise APIError(
                api_name="perplexity",
                error_message=f"Failed to research threats: {str(e)}"
            )
    
    def _parse_research_response(self, data: Dict[str, Any]) -> str:
        """Parse Perplexity API response"""
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "No research data available")
        return "No research data available"


class MockDataClient:
    """Client for loading mock data from JSON files"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
    
    def load_mock_weather(self, file_path: str = "mock_weather_data.json") -> WeatherData:
        """Load mock weather data from JSON file"""
        try:
            file_path = self.data_dir / file_path
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return WeatherData(
                location=data.get("location", "Unknown"),
                temperature_f=data.get("temperature_f", 72.0),
                condition=data.get("condition", "Clear"),
                humidity_percent=data.get("humidity_percent"),
                wind_speed_mph=data.get("wind_speed_mph"),
                nws_alert=data.get("nws_alert"),
                timestamp=datetime.utcnow(),
                source="mock"
            )
        except Exception as e:
            raise APIError(
                api_name="mock_weather",
                error_message=f"Failed to load mock weather data: {str(e)}"
            )
    
    def load_mock_grid(self, file_path: str = "mock_grid_data.json") -> GridData:
        """Load mock grid data from JSON file"""
        try:
            file_path = self.data_dir / file_path
            with open(file_path, 'r') as f:
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
