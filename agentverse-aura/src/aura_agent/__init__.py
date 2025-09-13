"""
AURA Smart Home Management Agent for FetchAI AgentVerse

This agent provides intelligent smart home management capabilities including:
- Weather-based home preparation
- Voice call notifications via VAPI
- Smart home device control simulation
- Energy market optimization
"""

from .aura_agent import AURAAgent
from .models import HomeStatus, Homeowner, WeatherEvent
from .voice_service import AURAVoiceService
from .smart_home_simulator import SmartHomeSimulator

__version__ = "1.0.0"
__all__ = ["AURAAgent", "HomeStatus", "Homeowner", "WeatherEvent", "AURAVoiceService", "SmartHomeSimulator"]
